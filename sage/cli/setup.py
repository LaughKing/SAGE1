#!/usr/bin/env python3
"""
SAGE CLI Setup
设置CLI工具的必要依赖和配置
"""

import os
import sys
from pathlib import Path
import subprocess

def install_cli_dependencies():
    """安装CLI必要的依赖"""
    dependencies = [
        "typer>=0.9.0",
        "colorama>=0.4.0",
        "tabulate>=0.9.0",
        "pyyaml>=6.0",
    ]
    
    print("📦 Installing CLI dependencies...")
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ Installed {dep}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {dep}")
            return False
    
    return True

def create_config_directory():
    """创建配置目录和默认配置"""
    config_dir = Path.home() / ".sage"
    config_file = config_dir / "config.yaml"
    
    # 创建配置目录
    config_dir.mkdir(exist_ok=True)
    
    # 创建默认配置文件（如果不存在）
    if not config_file.exists():
        default_config = """# SAGE CLI Configuration
daemon:
  host: "127.0.0.1"
  port: 19001

output:
  format: "table"
  colors: true

monitor:
  refresh_interval: 5

# JobManager settings
jobmanager:
  timeout: 30
  retry_attempts: 3
"""
        config_file.write_text(default_config)
        print(f"✅ Created default config: {config_file}")
    else:
        print(f"ℹ️  Config already exists: {config_file}")

def main():
    """主函数"""
    print("🚀 Setting up SAGE CLI...")
    
    # 安装依赖
    if not install_cli_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # 创建配置
    create_config_directory()
    
    print("\n✅ SAGE CLI setup completed!")
    print("\n📋 Next steps:")
    print("1. Run 'sage --help' to see available commands")
    print("2. Run 'sage deploy start' to start the system")
    print("3. Run 'sage job list' to see running jobs")
    print("\n💡 Use 'sage <command> --help' for detailed help")

if __name__ == "__main__":
    main()
