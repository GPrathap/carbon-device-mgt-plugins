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

var ws;
var attentionId = 6;
var meditationId = 5;
var poorSignalsId = 4;
var EEGPowers_Delta_ID = 7;
var EEGPowers_Theta_ID = 8;
var EEGPowers_LowAlpha_ID = 9;
var EEGPowers_HighAlpha_ID = 10;
var EEGPowers_LowBeta_ID = 11;
var EEGPowers_HighBeta_ID = 12;
var EEGPowers_LowGamma_ID = 13;
var EEGPowers_MidGamma_ID = 14;


var attention;
var attentionData = [];

var meditation;
var meditationData = [];

var poorSignals;
var poorSignalsData = [];

var eegPowers;

var EEGPowers_Delta = [];
var EEGPowers_Theta = [];
var EEGPowers_LowAlpha = [];
var EEGPowers_HighAlpha = [];
var EEGPowers_LowBeta = [];
var EEGPowers_HighBeta = [];
var EEGPowers_LowGamma = [];
var EEGPowers_MidGamma = [];

var palette = new Rickshaw.Color.Palette({scheme: "classic9"});

$(window).load(function () {
    poorSignals = lineGraph("PoorSignalLevel", poorSignalsData);
    attention = lineGraph("AttentionLevel", attentionData);
    meditation = lineGraph("MeditationLevel", meditationData);
	eegPowers = multiLineGraph("EEGPowers", EEGPowers_Delta, EEGPowers_Theta, EEGPowers_LowAlpha,EEGPowers_HighAlpha,
        EEGPowers_LowBeta, EEGPowers_HighBeta, EEGPowers_LowGamma, EEGPowers_MidGamma);
    var websocketUrl = $("#div-chart").data("websocketurl");
    connect(websocketUrl);
});

$(window).unload(function () {
    disconnect();
});

function multiLineGraph(type, EEGPowersDelta, EEGPowersTheta, EEGPowersLowAlpha,EEGPowersHighAlpha,
						 EEGPowersLowBeta, EEGPowersHighBeta, EEGPowersLowGamma, EEGPowersMidGamma ) {
	var tNow = new Date().getTime() / 1000;
	for (var i = 0; i < 30; i++) {
        EEGPowers_Delta.push({
			x: tNow - (30 - i) * 15,
			y: parseFloat(0)
		});
        EEGPowers_Theta.push({
			x: tNow - (30 - i) * 15,
			y: parseFloat(0)
		});
        EEGPowers_LowAlpha.push({
			x: tNow - (30 - i) * 15,
			y: parseFloat(0)
		});
        EEGPowers_HighAlpha.push({
            x: tNow - (30 - i) * 15,
            y: parseFloat(0)
        });
        EEGPowers_LowBeta.push({
            x: tNow - (30 - i) * 15,
            y: parseFloat(0)
        });
        EEGPowers_HighBeta.push({
            x: tNow - (30 - i) * 15,
            y: parseFloat(0)
        });
        EEGPowers_LowGamma.push({
            x: tNow - (30 - i) * 15,
            y: parseFloat(0)
        });
        EEGPowers_MidGamma.push({
            x: tNow - (30 - i) * 15,
            y: parseFloat(0)
        });
	}


	var graph = new Rickshaw.Graph({
		element: document.getElementById("chart-" + type),
		width: $("#div-chart").width() - 50,
		height: 300,
		renderer: "line",
		padding: {top: 0.2, left: 0.0, right: 0.0, bottom: 0.2},
		xScale: d3.time.scale(),
		series: [
			{'color': palette.color(), 'data': EEGPowersDelta, 'name': "Delta"},
			{'color': palette.color(), 'data': EEGPowersTheta, 'name': "Theta"},
			{'color': palette.color(), 'data': EEGPowersLowAlpha, 'name': "LowAlpha"},
            {'color': palette.color(), 'data': EEGPowersHighAlpha, 'name': "HighAlpha"},
            {'color': palette.color(), 'data': EEGPowersLowBeta, 'name': "LowBeta"},
            {'color': palette.color(), 'data': EEGPowersHighBeta, 'name': "HighBeta"},
            {'color': palette.color(), 'data': EEGPowersLowGamma, 'name': "LowGamma"},
            {'color': palette.color(), 'data': EEGPowersMidGamma, 'name': "MidGamma"}
		]
	});

	graph.render();

	var xAxis = new Rickshaw.Graph.Axis.Time({
		graph: graph
	});

	xAxis.render();

	new Rickshaw.Graph.Legend({
		graph: graph,
		element: document.getElementById('legend-' + type)
	});

	var detail = new Rickshaw.Graph.HoverDetail({
		graph: graph
	});

	return graph;
}

function lineGraph(type, chartData) {
	var tNow = new Date().getTime() / 1000;
	for (var i = 0; i < 30; i++) {
		chartData.push({
			x: tNow - (30 - i) * 15,
			y: parseFloat(0)
		});
	}

	var graph = new Rickshaw.Graph({
		element: document.getElementById("chart-" + type),
		width: $("#div-chart").width() - 50,
		height: 300,
		renderer: "line",
		padding: {top: 0.2, left: 0.0, right: 0.0, bottom: 0.2},
		xScale: d3.time.scale(),
		series: [{
			'color': palette.color(),
			'data': chartData,
			'name': type
		}]
	});

	graph.render();

	var xAxis = new Rickshaw.Graph.Axis.Time({
		graph: graph
	});

	xAxis.render();

	new Rickshaw.Graph.Axis.Y({
		graph: graph,
		orientation: 'left',
		height: 300,
		tickFormat: Rickshaw.Fixtures.Number.formatKMBT,
		element: document.getElementById('y_axis')
	});

	new Rickshaw.Graph.Legend({
		graph: graph,
		element: document.getElementById('legend-' + type)
	});

	new Rickshaw.Graph.HoverDetail({
		graph: graph,
		formatter: function (series, x, y) {
			var date = '<span class="date">' + moment(x * 1000).format('Do MMM YYYY h:mm:ss a') + '</span>';
			var swatch = '<span class="detail_swatch" style="background-color: ' + series.color + '"></span>';
			return swatch + series.name + ": " + parseInt(y) + '<br>' + date;
		}
	});

	return graph;
}

//websocket connection
function connect(target) {
	if ('WebSocket' in window) {
		ws = new WebSocket(target);
	} else if ('MozWebSocket' in window) {
		ws = new MozWebSocket(target);
	} else {
		console.log('WebSocket is not supported by this browser.');
	}
	if (ws) {
		ws.onmessage = function (event) {
                        console.log(event.data);
			var dataPoint = JSON.parse(event.data);
			if (dataPoint) {
				var time = parseInt(dataPoint[0]) / 1000;
					    graphUpdate(attentionData, time, dataPoint[attentionId], attention);
						graphUpdate(meditationData, time, dataPoint[meditationId], meditation);
                        graphUpdate(poorSignalsData, time, dataPoint[poorSignalsId], poorSignals);
						dataUpdate(EEGPowers_Delta, time, dataPoint[EEGPowers_Delta_ID]);
						dataUpdate(EEGPowers_Theta, time, dataPoint[EEGPowers_Theta_ID]);
						dataUpdate(EEGPowers_LowAlpha, time, dataPoint[EEGPowers_LowAlpha_ID]);
                        dataUpdate(EEGPowers_HighAlpha, time, dataPoint[EEGPowers_HighAlpha_ID]);
                        dataUpdate(EEGPowers_LowBeta, time, dataPoint[EEGPowers_LowBeta_ID]);
                        dataUpdate(EEGPowers_HighBeta, time, dataPoint[EEGPowers_HighBeta_ID]);
                        dataUpdate(EEGPowers_LowGamma, time, dataPoint[EEGPowers_LowGamma_ID]);
                        dataUpdate(EEGPowers_MidGamma, time, dataPoint[EEGPowers_MidGamma_ID]);
						eegPowers.update();
				}
			}
		};
}

function graphUpdate(chartData, xValue, yValue, graph) {
	chartData.push({
		x: parseInt(xValue),
		y: parseFloat(yValue)
	});
	chartData.shift();
	graph.update();
}

function dataUpdate(chartData, xValue, yValue) {
	chartData.push({
		x: parseInt(xValue),
		y: parseFloat(yValue)
	});
	chartData.shift();
}

function disconnect() {
    if (ws != null) {
        ws.close();
        ws = null;
    }
}
