from setuptools import find_packages, setup

setup(
    name="test-package",
    version="1.0.0",
    description="Test package for setup.py parsing",
    author="Test Author",
    author_email="test@example.com",
    license="MIT",
    python_requires=">=3.7",
    packages=find_packages(),
    install_requires=[
        "requests>=2.0.0",
        "flask>=2.0.0",
        "redis[hiredis]>=4.0.0",
        "importlib-metadata; python_version < '3.8'"
    ],
    extras_require={
        "dev": [
            "black==22.3.0",
            "flake8>=3.9.0",
            "mypy>=0.900"
        ],
        "aws": [
            "boto3>=1.20.0",
            "s3transfer>=0.5.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "test-cli=test_package.cli:main",
            "serve=test_package.server:run"
        ]
    }
) 