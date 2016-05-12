/*
 * Copyright (c) 2016, WSO2 Inc. (http://www.wso2.org) All Rights Reserved.
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
 * KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

package org.wso2.carbon.mdm.services.android.bean;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;

import java.io.Serializable;

/**
 * This class represents the information of uninstall application operation.
 */
@ApiModel(value = "ApplicationUninstallation",
        description = "This class carries all information related to application uninstallation.")
public class ApplicationUninstallation extends AndroidOperation implements Serializable {

    @ApiModelProperty(name = "appIdentifier", value = "The package name of the application to be uninstalled.", required = true)
	private String appIdentifier;

    @ApiModelProperty(name = "type", value = "The type of the application. The following types of applications " +
        "are supported: enterprise, public and webapp.", required = true)
	private String type;

    @ApiModelProperty(name = "url", value = "The URL of the application.", required = true)
	private String url;

    @ApiModelProperty(name = "name", value = "The name of the application.", required = true)
	private String name;

	public String getAppIdentifier() {
		return appIdentifier;
	}

	public void setAppIdentifier(String appIdentifier) {
		this.appIdentifier = appIdentifier;
	}

	public String getType() {
		return type;
	}

	public void setType(String type) {
		this.type = type;
	}

	public String getUrl() {
		return url;
	}

	public void setUrl(String url) {
		this.url = url;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}
}
