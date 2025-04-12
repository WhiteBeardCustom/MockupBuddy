from setuptools import setup, find_packages

setup(
    name="mockupbuddy",
    version="0.8.0",
    description="MockupBuddy - Desktop mockup generator using PySide6",
    author="Nick Trautman",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "PySide6",
        "Pillow"
    ],
    entry_points={
        "gui_scripts": [
            "mockupbuddy = MockupBuddy.MockupBuddy_PySide6_v0.8:main"
        ]
    },
    python_requires=">=3.8",
)