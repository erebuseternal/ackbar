#!/bin/bash
wget https://lilablobssc.blob.core.windows.net/models/camera_traps/megadetector/saved_model_normalized_megadetector_v3_tf19.tar.gz 
mkdir mega_detector_v3
tar -xf saved_model_normalized_megadetector_v3_tf19.tar.gz -C  mega_detector_v3