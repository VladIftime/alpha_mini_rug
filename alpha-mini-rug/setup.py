from setuptools import setup, find_packages

setup(
    name="alpha_mini_rug",
    version="0.7.0",
    description="Alpha Mini Robot wrapper for the RUG Social Robotics Lab",
    author="RUG Social Robotics Lab",
    author_email="socialrobotics@rug.nl",
    url="https://srl-rug.github.io/SRL_Website/",
    packages=find_packages(),
    install_requires=[
        "txaio",
        "autobahn",
        "numpy",
        "opencv-python",
        "opencv-contrib-python",
        "service_identity",
        "SpeechRecognition",
        "matplotlib",
        "wave",
        "msgpack",
    ],
)
