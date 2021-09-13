from setuptools import setup, find_packages

setup(
    name = "oolongTool",
    version = "0.1.1",
    keywords = ("pip", "oolongTool", "oolong"),
    description = "tiny tools in using slurm cluster",
    long_description = "this is a project for collecting some useful tools",
    license = "MIT Licence",

    url = "https://github.com/Suchun-sv/ClusterTools",
    author = "suchun",
    author_email = "2594405419@qq.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = [],
    entry_points={
        'console_scripts': [
            'PostMessage = oolongTool.PostMessage:main'
        ]
    }
)