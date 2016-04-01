/*
 * Copyright (c) 2015, WSO2 Inc. (http://www.wso2.org) All Rights Reserved.
 *
 * WSO2 Inc. licenses this file to you under the Apache License,
 * Version 2.0 (the "License"); you may not use this file except
 * in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

package org.wso2.carbon.device.mgt.iot.virtualfirealarm.plugin.internal;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.osgi.framework.BundleContext;
import org.osgi.framework.ServiceRegistration;
import org.osgi.service.component.ComponentContext;
import org.wso2.carbon.device.mgt.common.spi.DeviceManagementService;
import org.wso2.carbon.device.mgt.iot.virtualfirealarm.plugin.exception.VirtualFirealarmDeviceMgtPluginException;
import org.wso2.carbon.device.mgt.iot.virtualfirealarm.plugin.impl.VirtualFireAlarmManagerService;
import org.wso2.carbon.device.mgt.iot.virtualfirealarm.plugin.impl.util.VirtualFireAlarmUtils;

/**
 * @scr.component name="org.wso2.carbon.device.mgt.iot.virtualfirealarm.plugin.internal
 * .VirtualFirealarmManagementServiceComponent"
 * immediate="true"
 */
public class VirtualFirealarmManagementServiceComponent {

    private static final Log log = LogFactory.getLog(VirtualFirealarmManagementServiceComponent.class);
    private ServiceRegistration firealarmServiceRegRef;

    protected void activate(ComponentContext ctx) {
        if (log.isDebugEnabled()) {
            log.debug("Activating Virtual Firealarm Device Management Service Component");
        }
        try {
            BundleContext bundleContext = ctx.getBundleContext();
            firealarmServiceRegRef = bundleContext.registerService(DeviceManagementService.class.getName(),
                                                  new VirtualFireAlarmManagerService(), null);
            String setupOption = System.getProperty("setup");
            if (setupOption != null) {
                if (log.isDebugEnabled()) {
                    log.debug("-Dsetup is enabled. Iot Device management repository schema initialization is about " +
                                      "to begin");
                }
                try {
                    VirtualFireAlarmUtils.setupDeviceManagementSchema();
                } catch (VirtualFirealarmDeviceMgtPluginException e) {
                    log.error("Exception occurred while initializing device management database schema", e);
                }
            }
            if (log.isDebugEnabled()) {
                log.debug("Virtual Firealarm Device Management Service Component has been successfully activated");
            }
        } catch (Throwable e) {
            log.error("Error occurred while activating Virtual Firealarm Device Management Service Component", e);
        }
    }

    protected void deactivate(ComponentContext ctx) {
        if (log.isDebugEnabled()) {
            log.debug("De-activating Virtual Firealarm Device Management Service Component");
        }
        try {
            if (firealarmServiceRegRef != null) {
                firealarmServiceRegRef.unregister();
            }
            if (log.isDebugEnabled()) {
                log.debug("Virtual Firealarm Device Management Service Component has been successfully de-activated");
            }
        } catch (Throwable e) {
            log.error("Error occurred while de-activating Virtual Firealarm Device Management bundle", e);
        }
    }
}