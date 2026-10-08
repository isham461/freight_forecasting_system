import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, mean_absolute_percentage_error
from lightgbm import LGBMRegressor
from xgboost import XGBRegressor

class NaivePersistence:
    def __init__(self, col_idx):
        self.col_idx = col_idx
    def fit(self, X, y):
        pass
    def predict(self, X):
        return X[:, self.col_idx]

def evaluate_models(X, y, models, tscv):
    results = {name: {'mae': [], 'rmse': [], 'mape': []} for name in models.keys()}
    
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y.iloc[train_idx].values, y.iloc[test_idx].values
        
        # Scale the data (except for Naive model, which will pick up raw Capesize_Price manually if needed, 
        # but to keep it simple, we pass unscaled Capesize_Price to Naive if we know its index. 
        # Actually, let's scale X for ML models, and use raw X for naive)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        for name, model in models.items():
            if name == 'Naive_Persistence':
                preds = model.predict(X_test)
            else:
                model.fit(X_train_scaled, y_train)
                preds = model.predict(X_test_scaled)
                
            results[name]['mae'].append(mean_absolute_error(y_test, preds))
            results[name]['rmse'].append(root_mean_squared_error(y_test, preds))
            results[name]['mape'].append(mean_absolute_percentage_error(y_test, preds))
            
    # Aggregate results
    agg_results = {}
    for name in models.keys():
        agg_results[name] = {
            'MAE': np.mean(results[name]['mae']),
            'RMSE': np.mean(results[name]['rmse']),
            'MAPE': np.mean(results[name]['mape'])
        }
    return agg_results

def main():
    print("Loading data...")
    df = pd.read_csv('data/featured_freight_data.csv')
    # Drop Date column for training as it's not a numeric feature
    df_features = df.drop(columns=['Date'])
    
    horizons = {
        '7-Day': 'target_7d',
        '14-Day': 'target_14d',
        '30-Day': 'target_30d'
    }
    
    all_targets = list(horizons.values())
    
    tscv = TimeSeriesSplit(n_splits=5)
    final_artifacts = {}
    
    # Identify index of 'Capesize_Price' for Naive model
    features_base = [c for c in df_features.columns if c not in all_targets]
    capesize_idx = features_base.index('Capesize_Price')
    
    for horizon_name, target_col in horizons.items():
        print(f"\n=========================================")
        print(f"Training for {horizon_name} Horizon ({target_col})")
        print(f"=========================================")
        
        # Drop rows where target is NaN
        df_horizon = df.dropna(subset=[target_col]).copy()
        
        # Further drop any remaining NaNs caused by lagging
        df_horizon = df_horizon.dropna()
        
        X_df = df_horizon[features_base]
        y = df_horizon[target_col]
        
        X = X_df.values
        
        models = {
            'Naive_Persistence': NaivePersistence(col_idx=capesize_idx),
            'Ridge_Regression': Ridge(alpha=1.0),
            'LightGBM': LGBMRegressor(n_estimators=100, random_state=42, verbose=-1),
            'XGBoost': XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
        }
        
        results = evaluate_models(X, y, models, tscv)
        
        best_model_name = None
        best_mape = float('inf')
        
        print(f"{'Model':<20} | {'MAE':<10} | {'RMSE':<10} | {'MAPE':<10}")
        print("-" * 55)
        for name, metrics in results.items():
            print(f"{name:<20} | {metrics['MAE']:<10.2f} | {metrics['RMSE']:<10.2f} | {metrics['MAPE']:.4%}")
            
            # Select best model based on MAPE, excluding Naive
            if name != 'Naive_Persistence' and metrics['MAPE'] < best_mape:
                best_mape = metrics['MAPE']
                best_model_name = name
                
        print(f"\nBest ML Model for {horizon_name}: {best_model_name} (MAPE: {best_mape:.4%})")
        
        # Retrain best model on full horizon dataset
        print(f"Retraining {best_model_name} on full dataset for {horizon_name}...")
        final_scaler = StandardScaler()
        X_scaled = final_scaler.fit_transform(X)
        
        best_model = models[best_model_name]
        best_model.fit(X_scaled, y.values)
        
        final_artifacts[horizon_name] = {
            'model': best_model,
            'scaler': final_scaler,
            'features': features_base
        }
        
    print("\nSaving final model artifacts...")
    joblib.dump(final_artifacts, 'models/freight_forecaster.joblib')
    print("Saved to models/freight_forecaster.joblib")

if __name__ == "__main__":
    main()
