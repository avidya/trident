/**
 * Created by wangyang on 2015/1/6.
 */
/**
 * 打印
 * @return {void}
 * @author wangyang
 * @version 2014-1-6
 * @since 2014-1-6
 */
define(function(require, exports, module) {
	var $dispatcher = $("#dispatcher");
	var Column = require('highCharts');
	var Util = require('util'), util = new Util();
	var DatePicker = require('datePicker'), dtPicker = new DatePicker();
	var Dialog = require('dialog'), dialog = new Dialog();
	require('formatdate');
	var getUrl = $dispatcher.attr('data-getUrl');
	var Main = {
		initLeftNav : function() {
			var urlStatus = false;
			$('.leftNav li').each(function() {
				var me = $(this);
				var url = window.location.href;
				var loUrl = me.find('a').attr('href');
				if ((url + '/').indexOf(loUrl) > -1 && loUrl != '') {
					me.addClass('active').siblings('li').removeClass('active');
					urlStatus=true;
				} else {
					me.removeClass('active');
				}

			});
			if (!urlStatus) {
				$('.leftNav li').eq(0).addClass('active');
			}
		},
		initColumn : function() {
/**
			$("#createTime").val($.formatDate(new Date(), 'yyyy-MM-dd'));
			$("#startTime").val($.formatDate(new Date(), 'yyyy-MM-dd HH'));
			$("#endTime").val($.formatDate(new Date(), 'yyyy-MM-dd HH'));
*/
			//时间空间面板切换
			$('body').delegate('#timeChange.normal', 'click', function() {
				var me = $(this);
				$('.timeDiv').toggle();
				me.text('[查看概览]');
				me.attr('class', 'li_btn changeBtn detail');
				$("#createTime").val($.formatDate(new Date(), 'yyyy-MM-dd'));
				$('#time_type').val('1');
			});
			$('body').delegate('#timeChange.detail', 'click', function() {
				var me = $(this);
				$('.timeDiv').toggle();
				me.text('[查看详细]');
				me.attr('class', 'li_btn changeBtn normal');
				$("#startTime").val($.formatDate(new Date(), 'yyyy-MM-dd HH'));
				$("#endTime").val($.formatDate(new Date(), 'yyyy-MM-dd HH'));
				$('#time_type').val('0');
			});
			//时间控件
			$("#createTime").on("click focus", function() {
				dtPicker.initByCfg({
					maxDate : $.formatDate(new Date(), 'yyyy-MM-dd'),
					dateFmt : 'yyyy-MM-dd'
				});
			});
			$("#startTime").on("click focus", function() {
				dtPicker.initByCfg({
					maxDate : $.formatDate(new Date(), 'yyyy-MM-dd'),
					dateFmt : 'yyyy-MM-dd HH'
				});
			});
			$("#endTime").on("click focus", function() {
				dtPicker.initByCfg({
					maxDate : $.formatDate(new Date(), 'yyyy-MM-dd'),
					dateFmt : 'yyyy-MM-dd HH'
				});
			});
			/**
			//模式切换
			$('body').delegate('.act_title.now', 'click', function() {
				var me = $(this);
				me.siblings('.action_ul').find('.actionDate').toggle();
				me.text('[切换到详细模式]');
				me.attr('class', 'act_title history');
			});
			$('body').delegate('.act_title.history', 'click', function() {
				var me = $(this);
				me.siblings('.action_ul').find('.actionDate').toggle();
				me.text('[切换到历史模式]');
				me.attr('class', 'act_title now');
			});
			*/
			$.commonAjax({
				url:getUrl,
				type : 'post',
				data : {
					start_time : Date.parse($("#startTime").val().split(" ")[0])/1000  - 8*60*60 + $("#startTime").val().split(" ")[1] * 3600,
					end_time : Date.parse($("#endTime").val().split(" ")[0])/1000  - 8*60*60 + $("#endTime").val().split(" ")[1] * 3600,
					data_time: Date.parse($("#createTime").val())/1000 - 8*60*60,
					timeType:  $("#time_type").val()
				},
				success : function(re) {
					for (var i = 0; i < re.length; i++) {
						var item = re[i];
						Column.initConfig($('#con' + (i + 1)), {
							title : item.title,
							subtitle : item.subtitle,
							categories : item.categories,
							yAxis_text : item.yAxis_text,
							seriesName : item.seriesName,
							seriesData : item.seriesData,
							yMax: item.yMax_value
						});
					}
				},
				error : function(msg, status) {
					alert(msg);
				}
			});
			
			//切换host
			$('body').delegate('.ips', 'click', function() {
				var load_url = Main.get_url($(this).attr('href_url'), false, 0);
				//alert(load_url);
				window.location = load_url;
			});
	
			$('body').delegate('.timeShift', 'click', function() {
				var load_url = Main.get_url("/vm?ip="+$("#ip").val()+"&app="+$("#app").val(), false, parseInt($(this).attr('time_shift')));
				window.location = load_url;
			});
						
		},
		init : function() {
			Main.initLeftNav();
			Main.initColumn();
		},
		
		get_url: function(base_url, same_host, time_shift){
			var data_time = Date.parse($("#createTime").val())/1000 - 8*60*60 + time_shift;
			var start_time_str = $("#startTime").val();
			var start_time = Date.parse(start_time_str.split(" ")[0])/1000 - 8*60*60 + start_time_str.split(" ")[1] * 3600 + time_shift
			var end_time_str = $("#endTime").val();
			var end_time = Date.parse(end_time_str.split(" ")[0])/1000 - 8*60*60 + end_time_str.split(" ")[1] * 3600 + time_shift
			var time_type = $("#time_type").val();
			var ip_encode = $("#ip").val();
			var app_encode = $("#app").val();

			var tp_url = base_url+"&start_time="+start_time+"&end_time="+end_time+"&data_time="+data_time+"&timeType="+time_type;
			if(same_host){
				tp_url = tp_url+"&ip="+ip_encode+"&app="+app_encode;
			}
			return tp_url;
		}
	};
	Main.init();
});
