"""
Train Prophet-based Forecasting Model
Trains time series forecasting models for inventory prediction
"""

import pandas as pd
import numpy as np
from pathlib import Path
from prophet import Prophet
import joblib
from datetime import datetime, timedelta
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
import json
from tqdm import tqdm

# Paths
DATA_DIR = Path(__file__).parent.parent / "warehouse"
MODEL_DIR = Path(__file__).parent.parent / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def load_sales_data() -> pd.DataFrame:
    """Load sales history data"""
    print("Loading sales data...")
    sales_path = DATA_DIR / "sales_history.csv"
    
    if not sales_path.exists():
        raise FileNotFoundError(
            f"Sales data not found at {sales_path}. "
            "Run generate_warehouse_data.py first."
        )
    
    df = pd.read_csv(sales_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    print(f"✓ Loaded {len(df):,} sales records")
    
    return df


def prepare_training_data(
    sales_df: pd.DataFrame,
    sku: str,
    location: str
) -> pd.DataFrame:
    """
    Prepare data for Prophet training
    
    Args:
        sales_df: Sales history dataframe
        sku: Product SKU
        location: Store location
        
    Returns:
        DataFrame with 'ds' (date) and 'y' (quantity) columns
    """
    # Filter for specific SKU and location
    filtered = sales_df[
        (sales_df['sku'] == sku) & (sales_df['location'] == location)
    ].copy()
    
    if len(filtered) == 0:
        return pd.DataFrame(columns=['ds', 'y'])
    
    # Aggregate by date
    daily = filtered.groupby(
        filtered['timestamp'].dt.date
    ).agg({
        'quantity': 'sum'
    }).reset_index()
    
    daily.columns = ['ds', 'y']
    daily['ds'] = pd.to_datetime(daily['ds'])
    
    return daily


def train_prophet_model(
    training_data: pd.DataFrame,
    sku: str,
    location: str
) -> tuple:
    """
    Train Prophet model for a specific SKU/location
    
    Args:
        training_data: Prepared training data
        sku: Product SKU
        location: Store location
        
    Returns:
        Tuple of (model, metrics)
    """
    if len(training_data) < 14:
        print(f"  ⚠ Insufficient data for {sku} in {location} (only {len(training_data)} days)")
        return None, None
    
    # Split into train/test (80/20)
    split_idx = int(len(training_data) * 0.8)
    train = training_data[:split_idx]
    test = training_data[split_idx:]
    
    # Initialize Prophet model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode='multiplicative',
        changepoint_prior_scale=0.05,
        seasonality_prior_scale=10.0
    )
    
    # Train model
    model.fit(train)
    
    # Evaluate on test set
    if len(test) > 0:
        future_test = test[['ds']]
        forecast_test = model.predict(future_test)
        
        # Calculate metrics
        mape = mean_absolute_percentage_error(test['y'], forecast_test['yhat'])
        rmse = np.sqrt(mean_squared_error(test['y'], forecast_test['yhat']))
        
        metrics = {
            "sku": sku,
            "location": location,
            "training_samples": len(train),
            "test_samples": len(test),
            "mape": float(mape),
            "rmse": float(rmse),
            "trained_at": datetime.now().isoformat()
        }
    else:
        metrics = {
            "sku": sku,
            "location": location,
            "training_samples": len(train),
            "test_samples": 0,
            "mape": None,
            "rmse": None,
            "trained_at": datetime.now().isoformat()
        }
    
    return model, metrics


def train_all_models(
    sales_df: pd.DataFrame,
    max_models: int = 50
) -> dict:
    """
    Train models for top SKU/location combinations
    
    Args:
        sales_df: Sales history dataframe
        max_models: Maximum number of models to train
        
    Returns:
        Dictionary of training metrics
    """
    print(f"\nTraining up to {max_models} forecasting models...")
    
    # Find top SKU/location combinations by sales volume
    top_combinations = sales_df.groupby(['sku', 'location']).agg({
        'quantity': 'sum'
    }).reset_index().sort_values('quantity', ascending=False).head(max_models)
    
    print(f"Selected {len(top_combinations)} SKU/location combinations")
    
    all_metrics = []
    models_trained = 0
    
    for idx, row in tqdm(
        top_combinations.iterrows(),
        total=len(top_combinations),
        desc="Training models"
    ):
        sku = row['sku']
        location = row['location']
        
        # Prepare training data
        training_data = prepare_training_data(sales_df, sku, location)
        
        # Train model
        model, metrics = train_prophet_model(training_data, sku, location)
        
        if model is not None:
            # Save model
            model_filename = f"prophet_{sku}_{location.replace(' ', '_')}.pkl"
            model_path = MODEL_DIR / model_filename
            joblib.dump(model, model_path)
            
            metrics['model_file'] = model_filename
            all_metrics.append(metrics)
            models_trained += 1
    
    print(f"\n✓ Trained {models_trained} models successfully")
    
    # Save metrics
    metrics_path = MODEL_DIR / "training_metrics.json"
    with open(metrics_path, 'w') as f:
        json.dump(all_metrics, f, indent=2)
    
    print(f"✓ Saved training metrics to {metrics_path}")
    
    # Calculate average performance
    valid_mapes = [m['mape'] for m in all_metrics if m['mape'] is not None]
    if valid_mapes:
        avg_mape = np.mean(valid_mapes)
        print(f"\nAverage MAPE: {avg_mape:.2%}")
        print(f"Forecast Accuracy: {(1 - avg_mape) * 100:.1f}%")
    
    return {
        "models_trained": models_trained,
        "metrics": all_metrics,
        "average_mape": np.mean(valid_mapes) if valid_mapes else None
    }


def train_baseline_model(sales_df: pd.DataFrame) -> None:
    """
    Train a baseline model for general forecasting
    Uses aggregated data across all SKUs and locations
    """
    print("\nTraining baseline model...")
    
    # Aggregate all sales by date
    daily_total = sales_df.groupby(
        sales_df['timestamp'].dt.date
    ).agg({
        'quantity': 'sum'
    }).reset_index()
    
    daily_total.columns = ['ds', 'y']
    daily_total['ds'] = pd.to_datetime(daily_total['ds'])
    
    # Train Prophet model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode='multiplicative'
    )
    
    model.fit(daily_total)
    
    # Save baseline model
    baseline_path = MODEL_DIR / "prophet_baseline.pkl"
    joblib.dump(model, baseline_path)
    
    print(f"✓ Saved baseline model to {baseline_path}")


def generate_sample_forecast(
    sales_df: pd.DataFrame,
    sku: str = None,
    location: str = None,
    days: int = 30
) -> None:
    """
    Generate a sample forecast to verify models work
    
    Args:
        sales_df: Sales history dataframe
        sku: Product SKU (optional, uses first available)
        location: Store location (optional, uses first available)
        days: Number of days to forecast
    """
    print("\nGenerating sample forecast...")
    
    # Get first SKU/location if not specified
    if sku is None or location is None:
        top_combo = sales_df.groupby(['sku', 'location']).agg({
            'quantity': 'sum'
        }).reset_index().sort_values('quantity', ascending=False).iloc[0]
        
        sku = top_combo['sku']
        location = top_combo['location']
    
    print(f"  SKU: {sku}")
    print(f"  Location: {location}")
    
    # Load model
    model_filename = f"prophet_{sku}_{location.replace(' ', '_')}.pkl"
    model_path = MODEL_DIR / model_filename
    
    if not model_path.exists():
        print(f"  ⚠ Model not found: {model_filename}")
        return
    
    model = joblib.load(model_path)
    
    # Generate forecast
    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)
    
    # Get last 7 days of historical and next 7 days of forecast
    recent_forecast = forecast.tail(days + 7)
    
    print(f"\n  Forecast for next {days} days:")
    print(f"  Total predicted demand: {forecast.tail(days)['yhat'].sum():.0f} units")
    print(f"  Average daily demand: {forecast.tail(days)['yhat'].mean():.1f} units")
    print(f"  Confidence interval: [{forecast.tail(days)['yhat_lower'].mean():.1f}, {forecast.tail(days)['yhat_upper'].mean():.1f}]")
    
    # Determine trend
    recent_trend = forecast.tail(days)['trend'].values
    if recent_trend[-1] > recent_trend[0] * 1.05:
        trend = "increasing"
    elif recent_trend[-1] < recent_trend[0] * 0.95:
        trend = "decreasing"
    else:
        trend = "stable"
    
    print(f"  Trend: {trend}")


def main():
    """Main training pipeline"""
    print("=" * 60)
    print("ML MODEL TRAINING - PROPHET FORECASTING")
    print("=" * 60)
    
    # Load data
    sales_df = load_sales_data()
    
    # Train baseline model
    train_baseline_model(sales_df)
    
    # Train specific models
    results = train_all_models(sales_df, max_models=50)
    
    # Generate sample forecast
    generate_sample_forecast(sales_df, days=30)
    
    print("\n" + "=" * 60)
    print("MODEL TRAINING COMPLETE")
    print("=" * 60)
    print(f"\nModels saved in: {MODEL_DIR}")
    print(f"Total models: {results['models_trained']}")
    
    if results['average_mape']:
        print(f"Average forecast accuracy: {(1 - results['average_mape']) * 100:.1f}%")
    
    print("\n✓ Models are ready for use by the forecast agent")


if __name__ == "__main__":
    main()
