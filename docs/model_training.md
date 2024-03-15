# Model Training Guide

## Overview

This guide describes a simple process to [fine-tune](https://stats.stackexchange.com/a/387095) the existing spaghetti detecting model's weights using new images from your printer setup.

If you want to try your hand at improving the Spaghetti Detective's detecting ability for your setup, or if you just want to learn how to train a useful object detection model with a lot of the setup handled for you, read on!

## When to train

Model training can get pretty involved, and take a non-negligible amount of effort to do correctly. Even then, improvements in model quality aren't guaranteed. If you're here because you're having
detection issues, make sure that you're following [optimal camera setup](https://www.thespaghettidetective.com/docs/optimal-camera-setup/) and have taken steps to [reduce false alarms](https://www.thespaghettidetective.com/docs/failure-detection-false-alarms/#what-can-i-do-to-minimize-the-chance-of-false-alarms) before diving into model training.

You may also be interested in adding new features to the detection model, such as new sensor information or different output detection categories. These aren't covered directly in this guide, but it may be helpful to walk through it anyways to
get a feel for the training process.

## The Training Process

"Model training" encompasses a pretty huge body of knowledge - we're going to condense it down into a quick guide. If you're unsure about the basics, there are [literally millions of resources](https://www.google.com/search?q=ml+model+training) available on the internet for you to learn more.

In this guide, we'll go over data collection and labeling, Darknet model fine-tuning, performance evaluation, and installation.

### Setup

We'll need to install a few tools first.

#### BBox-Label-Tool

We'll use this labeling tool to add bounding boxes to spaghetti in images:

```shell
sudo apt install python2.7 python-imaging-tk
pip install pillow
git clone https://github.com/puzzledqs/BBox-Label-Tool
```

#### Spaghetti Detective Repo

The repository contains model configuration details which we'll need for training.

```shell
git clone https://github.com/TheSpaghettiDetective/obico-server.git
cd obico-server && wget -O ml_api/model/model.weights $(cat ml_api/model/model.weights.url | tr -d '\r')
```

### Collect and Prepare Data

If you've been using The Spaghetti Detective at all, you'll have plenty of recorded video in the [time-lapses page](https://app.thespaghettidetective.com/prints/) of the web app. In order to fine-tune the model, we need videos of false positives (spaghetti was detected when there was none) and false negatives (there was spaghetti, but it wasn't detected). Go ahead and download a few of each, using the triple-dot menu at the top right of each video file.


Now that we have our data, we need to transform it into something we can use for training. As [Darknet](https://github.com/AlexeyAB/darknet) is an ML toolkit for training [YOLO](https://pjreddie.com/darknet/yolo/) models for object detection in still images, this requires sampling images from the videos, labeling the objects (i.e. spaghetti), and grouping the images by category (spaghetti / not spaghetti):

**A note on data quality:** the model only trains based on what you've given it. The more varied examples you have and the clearer the spaghetti, the better the result. If you're seeing no improvement (or worse performance), check to make sure your data is correctly annotated and categorized, and try increasing the size of your dataset.

1. Create two directories: `positives` and `negatives`.
2. Move the downloaded videos into these directories - videos with spaghetti go in the `positives` directory, and those without go in `negatives`.
4. For each video in `positives`, note the time that the print started visibly failing. You'll need this to extract positive spaghetti images.
5. Run `python ./BBox-Label-Tool/main.py`, and annotate the images with bounding boxes (see [here](https://texas-aerial-robotics.github.io/md_yoloTraining.html) for a more in depth tutorial).
6. Collect all the information you've given so far and split it into two new folders: `./train` and `./test`, with `train.txt` and `test.txt` files containing paths to image samples extracted from your positive and negative video samples (more details on structure [here](https://github.com/AlexeyAB/darknet#how-to-train-to-detect-your-custom-objects)).

**On Holdout:** [See here](https://vitalflux.com/hold-out-method-for-training-machine-learning-model/) for a description on why we hold out data. As we're only training a single model and not selecting from multiple, we only need a train and test dataset.

### Train the Model

At this point, we should have sets of images in the `./train` and `./test` folders, plus annotations and labels where there's spaghetti. Before we start training, let's tweak a couple settings in the model config:

```shell
vim ml_api/model/model.cfg
```

Lower the learning rate to 0.0005 so that we don't lose a lot of weight information from the original training data. We want to refine the model, not train it from scratch.

With the new config saved, let's start training:

```shell
darknet detector train $1/obj.data ml_api/model/model.cfg ml_api/model/model.weights
```

You should see periodic reports of the training progress like so:
```
Region Avg IOU: 0.798363, Class: 0.893232, Obj: 0.700808, No Obj: 0.004567, Avg Recall: 1.000000, count: 8
Region Avg IOU: 0.800677, Class: 0.892181, Obj: 0.701590, No Obj: 0.004574, Avg Recall: 1.000000, count: 8

9002: 0.211667, 0.60730 avg, 0.001000 rate, 3.868000 seconds, 576128 images Loaded: 0.000000 seconds
```

Watch the `0.XXXXXX avg` value, and wait until it stops decreasing. At this point, the model has likely converged (see [here](https://github.com/AlexeyAB/darknet#when-should-i-stop-training) for details).

### Evaluate Performance

We don't yet know whether the model will perform better in the field. Let's start up the server running our new weights to see how it performs (you can also find more data on model development steps [here](https://github.com/TheSpaghettiDetective/orbico-server/blob/master/docs/model_development.md)):

```
docker-compose build ml_api
cp ./path_to_new_model_weights ml_api/model/model.weights
docker-compose run --service-ports --volume=./ml_api:/app ml_api /bin/bash -ic "gunicorn --bind 0.0.0.0:3333 --workers 1 wsgi"
```

In a separate shell, start a local server to provide your images: `cd path/to/test && python3 -m http.server`

Once the model server has loaded, you can try evaluating any of the images in your folder with:

http://localhost:3333/p/?img=http://localhost:8000/testimg.png

The model server will return a JSON blob with bounding box information for any spaghetti it detects. Try a few of your images and make sure that there are no more false positives/negatives in your data set. If you aren't satisfied with the results, you can try a couple things:

* Increase the learning rate in the model config. This will force the model to learn harder on your dataset, but risks [overfitting](https://elitedatascience.com/overfitting-in-machine-learning) and may perform worse in the real world.
* Use more (or different) training data - download more videos and extract and annotate them before training again.
* Try some of the suggestions [here](https://github.com/AlexeyAB/darknet#how-to-improve-object-detection).

### Contribute Improvements

Given that this guide is for fine-tuning the model to your specific printing setup, it's unlikely that it will perform better than the base model in the general case.

However, if you have suggestions or improvements to the overall quality of the model, please open a [new issue](https://github.com/TheSpaghettiDetective/orbico-server/issues/new/choose) where it can be discussed.
