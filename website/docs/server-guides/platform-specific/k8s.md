# Run obico-server on Kubernetes

Kubernetes, first introduced in 2014, has been fast becoming the new normal for installing cloud based software. K8S gives you a High Availability (HA) setup very easily.

Traditionally, Docker-Compose is used for running Obico-Server. Using K8S requires a much greater hand-on knowledge of linux to manage, so it won't be for the faint of heart. 

## Installing a K8S Cluster

It is worth noting that a fully managed/configured K8S environment is beyond they scope of this document and requires an in-depth knowledge of linux administration. Most cloud providers do offer some form of Kubernetes cluster to get started with, including:

- `AKS` - Azure Kubernetes Service
- `DOKS` - Digital Ocean Kubernetes Service
- `EKS` - Amazon Elastic Kubernetes Service

For more local installs, you have several options:

- `Docker Desktop` - Supports a K8S Configuration
- `Rancher Desktop` - RD was created as a replacement to Docker Desktop when the latter updated their license to be commercial only. It is one of the easier software to install a running K8S environment, but is intended mostly for development purposes.
- `K3S` - SUSE, The same people that made `Rancher` and `Rancher Desktop` are the brains behind K3S, a lightweight alternative to a traditional K8S configuration.
- `MiniKube`
- `MicroK8S`

If you are just interested in testing Obico Server through K8S, then the simplest route is going to be to use Rancher Desktop. For more long-term installations, K3S can be quickly installed.

### Rancher Desktop Quick Gotchas

By default, RD comes with the `containerd` engine enabled. In order to use RD, you will need to update the settings to change the engine to `Docker/Moby`. Otherwise docker commands will not work. Additionally, it's worth noting that RD & Docker Desktop do not work together, so you must fully disable Docker Desktop's service.

### K3S

K3S can be quickly installed with a quick one-liner command on most distributions:

```shell
curl -sfL https://get.k3s.io | sh -
```

This will create a one node K8S cluster that is immediately available for use with `kubectl` already installed. The K8S configuration file will be saved to `/etc/rancher/k3s/k3s.yaml`, which you can download to a local computer to execute K8S commands with.

## Installing Obico Server

### Repository

Unlike the Docker Compose installation, K8S does not require you work on the host computer. This means that you can checkout the repository wherever you want, so long as you've got kubectl configured. You will still need the repository, which you can download using:

```shell
git clone -b release https://github.com/TheSpaghettiDetective/obico-server.git
```

### Helm

The installation of Obico Server is done via a utility called `Helm`. This utility simplifies the installation of K8S environments. [How to Install Helm](https://helm.sh/docs/intro/install/)

The Helm Charts for Obico Server are found in the `helm` folder of the git repository.

### Building Images

