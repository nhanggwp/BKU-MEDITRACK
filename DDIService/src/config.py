"""
Configuration Management for DDI Service
"""
import os
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ModelConfig:
    """Model configuration parameters"""
    input_dim: int = 515  # 512 fingerprint + 3 descriptors
    num_labels: int = 1317  # Updated TWOSIDES labels
    hidden_dim: int = 1024
    dropout: float = 0.4
    model_path: str = "./models/best_ddi_model.pt"


@dataclass
class TrainingConfig:
    """Training configuration parameters"""
    epochs: int = 10
    batch_size: int = 256
    learning_rate: float = 1e-3
    num_workers: int = 2
    device: str = "auto"  # auto, cuda, cpu
    
    # Loss function parameters
    focal_alpha: float = 2.0
    focal_gamma: float = 2.0
    
    # Scheduler parameters
    scheduler_patience: int = 2
    scheduler_factor: float = 0.5


@dataclass
class DataConfig:
    """Data configuration parameters"""
    dataset_name: str = "TWOSIDES"
    random_seed: int = 42
    n_bits: int = 512  # Fingerprint bits
    cache_dir: str = "./cache"
    use_cache: bool = True


@dataclass
class ServerConfig:
    """API server configuration parameters"""
    host: str = "0.0.0.0"
    port: int = 8001
    workers: int = 1
    reload: bool = False
    log_level: str = "info"
    
    # API parameters
    max_batch_size: int = 100
    default_top_k: int = 5
    request_timeout: float = 30.0


@dataclass
class DDIConfig:
    """Complete DDI service configuration"""
    model: ModelConfig
    training: TrainingConfig
    data: DataConfig
    server: ServerConfig
    
    # Environment
    environment: str = "development"  # development, production, testing
    debug: bool = False


def load_config(config_path: Optional[str] = None) -> DDIConfig:
    """
    Load configuration from file and environment variables
    
    Args:
        config_path: Path to YAML configuration file
        
    Returns:
        DDIConfig object with loaded configuration
    """
    # Default configuration
    config = DDIConfig(
        model=ModelConfig(),
        training=TrainingConfig(),
        data=DataConfig(),
        server=ServerConfig()
    )
    
    # Load from YAML file if provided
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            yaml_config = yaml.safe_load(f)
        
        # Update configuration from YAML
        config = update_config_from_dict(config, yaml_config)
        print(f"Loaded configuration from {config_path}")
    
    # Override with environment variables
    config = update_config_from_env(config)
    
    return config


def update_config_from_dict(config: DDIConfig, config_dict: Dict[str, Any]) -> DDIConfig:
    """Update configuration from dictionary"""
    
    if 'model' in config_dict:
        for key, value in config_dict['model'].items():
            if hasattr(config.model, key):
                setattr(config.model, key, value)
    
    if 'training' in config_dict:
        for key, value in config_dict['training'].items():
            if hasattr(config.training, key):
                setattr(config.training, key, value)
    
    if 'data' in config_dict:
        for key, value in config_dict['data'].items():
            if hasattr(config.data, key):
                setattr(config.data, key, value)
    
    if 'server' in config_dict:
        for key, value in config_dict['server'].items():
            if hasattr(config.server, key):
                setattr(config.server, key, value)
    
    # Update top-level fields
    for key in ['environment', 'debug']:
        if key in config_dict:
            setattr(config, key, config_dict[key])
    
    return config


def update_config_from_env(config: DDIConfig) -> DDIConfig:
    """Update configuration from environment variables"""
    
    # Model configuration
    if os.getenv('DDI_MODEL_PATH'):
        config.model.model_path = os.getenv('DDI_MODEL_PATH')
    
    if os.getenv('DDI_HIDDEN_DIM'):
        config.model.hidden_dim = int(os.getenv('DDI_HIDDEN_DIM'))
    
    if os.getenv('DDI_DROPOUT'):
        config.model.dropout = float(os.getenv('DDI_DROPOUT'))
    
    # Training configuration
    if os.getenv('DDI_EPOCHS'):
        config.training.epochs = int(os.getenv('DDI_EPOCHS'))
    
    if os.getenv('DDI_BATCH_SIZE'):
        config.training.batch_size = int(os.getenv('DDI_BATCH_SIZE'))
    
    if os.getenv('DDI_LEARNING_RATE'):
        config.training.learning_rate = float(os.getenv('DDI_LEARNING_RATE'))
    
    if os.getenv('DDI_DEVICE'):
        config.training.device = os.getenv('DDI_DEVICE')
    
    # Data configuration
    if os.getenv('DDI_DATASET'):
        config.data.dataset_name = os.getenv('DDI_DATASET')
    
    if os.getenv('DDI_CACHE_DIR'):
        config.data.cache_dir = os.getenv('DDI_CACHE_DIR')
    
    if os.getenv('DDI_USE_CACHE'):
        config.data.use_cache = os.getenv('DDI_USE_CACHE').lower() == 'true'
    
    # Server configuration
    if os.getenv('DDI_HOST'):
        config.server.host = os.getenv('DDI_HOST')
    
    if os.getenv('DDI_PORT'):
        config.server.port = int(os.getenv('DDI_PORT'))
    
    if os.getenv('DDI_WORKERS'):
        config.server.workers = int(os.getenv('DDI_WORKERS'))
    
    if os.getenv('DDI_LOG_LEVEL'):
        config.server.log_level = os.getenv('DDI_LOG_LEVEL')
    
    # Environment
    if os.getenv('DDI_ENVIRONMENT'):
        config.environment = os.getenv('DDI_ENVIRONMENT')
    
    if os.getenv('DDI_DEBUG'):
        config.debug = os.getenv('DDI_DEBUG').lower() == 'true'
    
    return config


def save_config(config: DDIConfig, config_path: str):
    """Save configuration to YAML file"""
    config_dict = asdict(config)
    
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    print(f"Configuration saved to {config_path}")


def get_device(device_config: str) -> str:
    """Get the actual device to use based on configuration"""
    if device_config == "auto":
        try:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            return "cpu"
    else:
        return device_config


def create_default_configs():
    """Create default configuration files for different environments"""
    
    # Development config
    dev_config = DDIConfig(
        model=ModelConfig(),
        training=TrainingConfig(epochs=5, batch_size=128),  # Faster for development
        data=DataConfig(),
        server=ServerConfig(reload=True, log_level="debug"),
        environment="development",
        debug=True
    )
    
    # Production config
    prod_config = DDIConfig(
        model=ModelConfig(),
        training=TrainingConfig(epochs=20, batch_size=512),  # More thorough for production
        data=DataConfig(),
        server=ServerConfig(workers=4, log_level="info"),
        environment="production",
        debug=False
    )
    
    # Testing config
    test_config = DDIConfig(
        model=ModelConfig(),
        training=TrainingConfig(epochs=2, batch_size=64),  # Fast for testing
        data=DataConfig(),
        server=ServerConfig(log_level="warning"),
        environment="testing",
        debug=False
    )
    
    # Create configs directory
    os.makedirs("./configs", exist_ok=True)
    
    # Save configurations
    save_config(dev_config, "./configs/development.yaml")
    save_config(prod_config, "./configs/production.yaml")
    save_config(test_config, "./configs/testing.yaml")
    
    print("Created default configuration files:")
    print("  ./configs/development.yaml")
    print("  ./configs/production.yaml")
    print("  ./configs/testing.yaml")


def print_config(config: DDIConfig):
    """Print configuration in a readable format"""
    print("DDI Service Configuration")
    print("=" * 50)
    
    print(f"Environment: {config.environment}")
    print(f"Debug: {config.debug}")
    
    print("\nModel Configuration:")
    print(f"  Input Dimension: {config.model.input_dim}")
    print(f"  Number of Labels: {config.model.num_labels}")
    print(f"  Hidden Dimension: {config.model.hidden_dim}")
    print(f"  Dropout: {config.model.dropout}")
    print(f"  Model Path: {config.model.model_path}")
    
    print("\nTraining Configuration:")
    print(f"  Epochs: {config.training.epochs}")
    print(f"  Batch Size: {config.training.batch_size}")
    print(f"  Learning Rate: {config.training.learning_rate}")
    print(f"  Device: {config.training.device}")
    print(f"  Focal Alpha: {config.training.focal_alpha}")
    print(f"  Focal Gamma: {config.training.focal_gamma}")
    
    print("\nData Configuration:")
    print(f"  Dataset: {config.data.dataset_name}")
    print(f"  Random Seed: {config.data.random_seed}")
    print(f"  Fingerprint Bits: {config.data.n_bits}")
    print(f"  Cache Directory: {config.data.cache_dir}")
    print(f"  Use Cache: {config.data.use_cache}")
    
    print("\nServer Configuration:")
    print(f"  Host: {config.server.host}")
    print(f"  Port: {config.server.port}")
    print(f"  Workers: {config.server.workers}")
    print(f"  Reload: {config.server.reload}")
    print(f"  Log Level: {config.server.log_level}")
    print(f"  Max Batch Size: {config.server.max_batch_size}")
    
    print("=" * 50)