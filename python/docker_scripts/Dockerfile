#Inherit from the latest jupyter scipy notebook
FROM jupyter/scipy-notebook

USER root

ENV DEBIAN_FRONTEND noninteractive

#Install ffmpeg to save animations from jupyter
RUN apt-get update && apt-get install -y  dc bc ffmpeg

#install the conda environment
USER jovyan
COPY environment.yml /home/jovyan/environment.yml
RUN conda init bash && bash && conda env create --file /home/jovyan/environment.yml --name submission

#Custom packages for student submissions of Final project.
RUN activate submission && pip install idx2numpy qit

#matplotlib default to prevent QT backend being used.
COPY matplotlibrc /home/jovyan/.matplotlib/matplotlibrc
ENV MATPLOTLIBRC /home/jovyan/.matplotlib/matplotlibrc
ENV CONDA_DEFAULT_ENV submission
RUN echo "conda activate submission" > ~/.bashrc
ENV PATH /opt/conda/envs/submission/bin:$PATH