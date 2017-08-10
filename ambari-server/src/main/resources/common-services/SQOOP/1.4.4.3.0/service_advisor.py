#!/usr/bin/env ambari-python-wrap
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# Python imports
import imp
import os
import traceback
import re
import socket
import fnmatch


from resource_management.core.logger import Logger

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STACKS_DIR = os.path.join(SCRIPT_DIR, '../../../stacks/')
PARENT_FILE = os.path.join(STACKS_DIR, 'service_advisor.py')

try:
  with open(PARENT_FILE, 'rb') as fp:
    service_advisor = imp.load_module('service_advisor', fp, PARENT_FILE, ('.py', 'rb', imp.PY_SOURCE))
except Exception as e:
  traceback.print_exc()
  print "Failed to load parent"

class SqoopServiceAdvisor(service_advisor.ServiceAdvisor):

  def __init__(self, *args, **kwargs):
    self.as_super = super(SqoopServiceAdvisor, self)
    self.as_super.__init__(*args, **kwargs)

    # Always call these methods
    self.modifyMastersWithMultipleInstances()
    self.modifyCardinalitiesDict()
    self.modifyHeapSizeProperties()
    self.modifyNotValuableComponents()
    self.modifyComponentsNotPreferableOnServer()
    self.modifyComponentLayoutSchemes()

  def modifyMastersWithMultipleInstances(self):
    """
    Modify the set of masters with multiple instances.
    Must be overriden in child class.
    """
    # Nothing to do
    pass

  def modifyCardinalitiesDict(self):
    """
    Modify the dictionary of cardinalities.
    Must be overriden in child class.
    """
    # Nothing to do
    pass

  def modifyHeapSizeProperties(self):
    """
    Modify the dictionary of heap size properties.
    Must be overriden in child class.
    """
    pass

  def modifyNotValuableComponents(self):
    """
    Modify the set of components whose host assignment is based on other services.
    Must be overriden in child class.
    """
    # Nothing to do
    pass

  def modifyComponentsNotPreferableOnServer(self):
    """
    Modify the set of components that are not preferable on the server.
    Must be overriden in child class.
    """
    # Nothing to do
    pass

  def modifyComponentLayoutSchemes(self):
    """
    Modify layout scheme dictionaries for components.
    The scheme dictionary basically maps the number of hosts to
    host index where component should exist.
    Must be overriden in child class.
    """
    # Nothing to do
    pass

  def getServiceComponentLayoutValidations(self, services, hosts):
    """
    Get a list of errors.
    Must be overriden in child class.
    """

    return []

  def getServiceConfigurationRecommendations(self, configurations, clusterData, services, hosts):
    """
    Entry point.
    Must be overriden in child class.
    """
    #Logger.info("Class: %s, Method: %s. Recommending Service Configurations." %
    #            (self.__class__.__name__, inspect.stack()[0][3]))

    recommender = SqoopRecommender()
    recommender.recommendSqoopConfigurationsFromHDP23(configurations, clusterData, services, hosts)



  def getServiceConfigurationsValidationItems(self, configurations, recommendedDefaults, services, hosts):
    """
    Entry point.
    Validate configurations for the service. Return a list of errors.
    The code for this function should be the same for each Service Advisor.
    """
    #Logger.info("Class: %s, Method: %s. Validating Configurations." %
    #            (self.__class__.__name__, inspect.stack()[0][3]))

    validator = SqoopValidator()
    # Calls the methods of the validator using arguments,
    # method(siteProperties, siteRecommendations, configurations, services, hosts)
    return validator.validateListOfConfigUsingMethod(configurations, recommendedDefaults, services, hosts, validator.validators)



class SqoopRecommender(service_advisor.ServiceAdvisor):
  """
  Sqoop Recommender suggests properties when adding the service for the first time or modifying configs via the UI.
  """

  def __init__(self, *args, **kwargs):
    self.as_super = super(SqoopRecommender, self)
    self.as_super.__init__(*args, **kwargs)


  def recommendSqoopConfigurationsFromHDP23(self, configurations, clusterData, services, hosts):
    putSqoopSiteProperty = self.putProperty(configurations, "sqoop-site", services)
    putSqoopEnvProperty = self.putProperty(configurations, "sqoop-env", services)

    enable_external_atlas_for_sqoop = False
    enable_atlas_hook = False
    servicesList = [service["StackServices"]["service_name"] for service in services["services"]]
    if 'sqoop-atlas-application.properties' in services['configurations'] and 'enable.external.atlas.for.sqoop' in services['configurations']['sqoop-atlas-application.properties']['properties']:
      enable_external_atlas_for_sqoop = services['configurations']['sqoop-atlas-application.properties']['properties']['enable.external.atlas.for.sqoop'].lower() == "true"

    if "ATLAS" in servicesList:
      putSqoopEnvProperty("sqoop.atlas.hook", "true")
    elif enable_external_atlas_for_sqoop:
      putSqoopEnvProperty("sqoop.atlas.hook", "true")
    else:
      putSqoopEnvProperty("sqoop.atlas.hook", "false")

    if 'sqoop-env' in configurations and 'sqoop.atlas.hook' in configurations['sqoop-env']['properties']:
      enable_atlas_hook = configurations['sqoop-env']['properties']['sqoop.atlas.hook'] == "true"
    elif 'sqoop-env' in services['configurations'] and 'sqoop.atlas.hook' in services['configurations']['sqoop-env']['properties']:
      enable_atlas_hook = services['configurations']['sqoop-env']['properties']['sqoop.atlas.hook'] == "true"

    if enable_atlas_hook:
      putSqoopSiteProperty('sqoop.job.data.publish.class', 'org.apache.atlas.sqoop.hook.SqoopHook')
    else:
      putSqoopSitePropertyAttribute = self.putPropertyAttribute(configurations, "sqoop-site")
      putSqoopSitePropertyAttribute('sqoop.job.data.publish.class', 'delete', 'true')



class SqoopValidator(service_advisor.ServiceAdvisor):
  """
  Sqoop Validator checks the correctness of properties whenever the service is first added or the user attempts to
  change configs via the UI.
  """

  def __init__(self, *args, **kwargs):
    self.as_super = super(SqoopValidator, self)
    self.as_super.__init__(*args, **kwargs)

    self.validators = []




