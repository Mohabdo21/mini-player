from setuptools import find_namespace_packages, setup

if __name__ == "__main__":
    setup(
        name="mini-player",
        version="1.0.0",
        packages=[
            "miniplayer",
            "miniplayer.core",
            "miniplayer.ui",
            "miniplayer.utils",
        ],
        package_dir={"miniplayer": "src/miniplayer"},
        package_data={"miniplayer": ["../icons/*", "../default_album.png"]},
        install_requires=["PyQt6>=6.0.0", "mutagen>=1.45.1"],
        entry_points={
            "console_scripts": [
                "mini-player=miniplayer.app:main",
            ],
        },
    )
