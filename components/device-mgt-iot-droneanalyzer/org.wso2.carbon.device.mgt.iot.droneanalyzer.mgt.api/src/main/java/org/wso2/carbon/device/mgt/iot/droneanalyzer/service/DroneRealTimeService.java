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
package org.wso2.carbon.device.mgt.iot.droneanalyzer.service;


import org.apache.commons.logging.LogFactory;
import org.wso2.carbon.device.mgt.iot.controlqueue.mqtt.MqttConfig;
import org.wso2.carbon.device.mgt.iot.controlqueue.xmpp.XmppConfig;
import org.wso2.carbon.device.mgt.iot.droneanalyzer.plugin.constants.DroneConstants;
import org.wso2.carbon.device.mgt.iot.droneanalyzer.service.transport.DroneAnalyzerXMPPConnector;
import org.wso2.carbon.device.mgt.iot.droneanalyzer.service.trasformer.MessageTransformer;

import javax.websocket.*;
import javax.websocket.server.ServerEndpoint;
import java.io.IOException;

@ServerEndpoint("/datastream/drone_status")
public class DroneRealTimeService {

    private static org.apache.commons.logging.Log log = LogFactory.getLog(DroneRealTimeService.class);
    private MessageTransformer messageController;
    private DroneAnalyzerXMPPConnector xmppConnector;

    public DroneRealTimeService() {
        messageController = new MessageTransformer();
        xmppConnector = new DroneAnalyzerXMPPConnector(messageController);

        if (XmppConfig.getInstance().isEnabled()){
            xmppConnector.connectLoginAndSetFilterOnReceiver();
        } else {
            log.warn("XMPP disabled in 'devicemgt-config.xml'. Hence, VirtualFireAlarmXMPPConnector not started.");
        }
    }


    /**
     *
     * @param session
     */
    @OnOpen
    public void onOpen(Session session){
        log.info(session.getId() + " has opened a connection");
        try {
            session.getBasicRemote().sendText("Connection Established");
        } catch (IOException e) {
            log.error( e.getMessage()+"\n"+ e);
        }
    }

    @OnMessage
    public void onMessage(String message, Session session){
        try {
            while(true){
                if((messageController !=null) && (!messageController.isEmptyQueue())){
                    String message1 = messageController.getMessage();
                    session.getBasicRemote().sendText(message1);
                }
                Thread.sleep(DroneConstants.MINIMUM_TIME_DURATION);
            }
        } catch (IOException ex) {
            log.error(ex.getMessage() + "\n" + ex);
        } catch (InterruptedException e) {
            log.error(e.getMessage(), e);
        }
    }

    @OnClose
    public void onClose(Session session){

        try {
            xmppConnector.disconnect();
            log.info("XMPP connection is disconnected");
        }
        catch (Exception e) {
            log.error(e.getMessage() + "\n" + e);
        }
        log.info("Session " + session.getId() + " has ended");
    }

    @OnError
    public void onError(Session session, Throwable t) {
        try {
            session.getBasicRemote().sendText("Connection closed");
            xmppConnector.disconnect();
            log.info("XMPP connection is disconnected");
        } catch (Exception e) {
            log.error(e.getMessage()+"\n"+ e);
        }
        log.info("Session " + session.getId() + " has ended");
    }

}