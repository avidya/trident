define(function(require, exports, module) {
	require('lib/highcharts/highcharts');
	var Column = {
		initConfig : function($ele, option) {
			Highcharts.setOptions({
				colors : ['#E84940']
			});
			$ele.highcharts({
				credits : {
					enabled : false
				},
				chart : {
					type : 'column'
				},
				title : {
					text : option.title
				},
				subtitle : {
					text : option.subtitle
				},
				xAxis : {
					tickColor : '#000',
					lineColor : '#000',
					lineWidth : 1,
					tickInterval : 5,
					categories : option.categories
				},
				yAxis : {
					lineColor : '#000',
					lineWidth : 1,
					min : 0,
					title : {
						text : option.yAxisText
					}
				},
				tooltip : {
					headerFormat : '<span style="font-size:10px">{point.key}</span><table>',
					pointFormat : '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' + '<td style="padding:0"><b>{point.y:.1f} mm</b></td></tr>',
					footerFormat : '</table>',
					shared : true,
					useHTML : true
				},
				plotOptions : {
					column : {
						pointPadding : 0.2,
						borderWidth : 0
					}
				},
				series : [{
					"name" : option.seriesName,
					"data" : option.seriesData
				}]
			});
		}
	};
	module.exports = Column;
});
