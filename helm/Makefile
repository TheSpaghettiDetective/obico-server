##############################
# Preliminary Configuration
##############################

BIN_PATH := bin

# As this Makefile is in the Helm Folder, We Have To Adjust Our Path
HELM_FOLDER := .

##############################
# Default Target
##############################
default: $(BIN_PATH)/values-local.yaml
	make helm-start

#################################
# Include Local Overrides
#################################
# You can manually edit `bin/overrides.mk` to use your preferred download agent.

# Only Include If Not Already Included (Will Cause Warnings Otherwise)
ifndef MAKEFILE_OVERRIDES
include $(BIN_PATH)/overrides.mk
endif

###########################################
# Post Overrides Configuration Defaults
###########################################

HELM_NAME ?= obico
HELM_CONFIG ?= bin/values-local.yaml

ifndef MAKEFILE_DOWNLOAD_COMMAND

ifneq (, $(shell which wget))
MAKEFILE_DOWNLOAD_COMMAND = wget -O $@
endif

ifneq (, $(shell which curl))
MAKEFILE_DOWNLOAD_COMMAND = curl -o $@
endif

endif

#################################
# Include Helm Helper
#################################
$(BIN_PATH)/helm.mk:
	$(MAKEFILE_DOWNLOAD_COMMAND) https://gitlab.com/twistersfury/utilities/-/raw/v2.1.6/make/helm.mk

# Only Include Helm If Overrides File Created
ifdef MAKEFILE_OVERRIDES
ifndef MAKEFILE_HELM
include $(BIN_PATH)/helm.mk
endif
endif

#################################
# Hard Files
#################################

$(BIN_PATH):
	mkdir -p $@

$(BIN_PATH)/values-local.yaml: | $(BIN_PATH)/overrides.mk
	@echo 'email:' >> $@
	@echo '  secret: false' >> $@
	@echo '' >> $@
	@echo 'pushover:' >> $@
	@echo '  secret: false' >> $@
	@echo '' >> $@
	@echo 'slack:' >> $@
	@echo '  secret: false' >> $@
	@echo '' >> $@
	@echo 'telegram:' >> $@
	@echo '  secret: false' >> $@
	@echo '' >> $@
	@echo 'twilio:' >> $@
	@echo '  secret: false' >> $@
	@echo '' >> $@
	@echo "Default $@ Local Values Created. Modify it or supply your own yaml configuration using 'HELM_CONFIG' in bin/overrides.mk"
	@echo ''

$(BIN_PATH)/overrides.mk: | $(BIN_PATH)
	@echo '# Do Not Remove ' > $@
	@echo 'MAKEFILE_OVERRIDES := true' >> $@
	@echo '' >> $@
	@echo '# Change Preferred Download Utility' >> $@
	@echo '# MAKEFILE_DOWNLOAD_COMMAND = curl -o $$@' >> $@
	@echo '# MAKEFILE_DOWNLOAD_COMMAND = wget -O $$@' >> $@
	@echo '' >> $@
	@echo '# Change Helm Values Override File' >> $@
	@echo '# HELM_CONFIG ?= bin/values-local.yaml' >> $@
	@echo ''
	@echo "Override file $@ Created. You will have to rerun the previous command."
	@echo '' && exit 1

$(BIN_PATH)/.build: ../docker-compose.yml ../backend/Dockerfile | $(BIN_PATH)
	docker-compose -f ../docker-compose.yml build
	touch $@

.PHONY: helm-start
helm-start: $(BIN_PATH)/.build
