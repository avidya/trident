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
	var subItemsUrl = $dispatcher.attr('data-subItemsUrl');
	var Util = require('util'), util = new Util();
	var DatePicker = require('datePicker'), dtPicker = new DatePicker();
	var Dialog = require('dialog'), dialog = new Dialog();
	require('formatdate');

/*	var sortUrl = $dispatcher.attr('data-sortUrl');
	var afterSort = $dispatcher.attr('data-afterUrl');*/
	var Main = {
		init : function() {
			Main.initLeftNav();
			Main.initPages();
			Main.pages();
		},
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
		initPages : function() {
			//明细和概览面板切换
			$('body').delegate('#timeChange.normal', 'click', function() {
				var me = $(this);
				$('.timeDiv').toggle();
				me.text('[查看概览]');
				me.attr('class', 'li_btn changeBtn detail');
				$('#time_type').val('1');
			});
			$('body').delegate('#timeChange.detail', 'click', function() {
				var me = $(this);
				$('.timeDiv').toggle();
				me.text('[查看详细]');
				me.attr('class', 'li_btn changeBtn normal');
				$('#time_type').val('0');
			});

			//明细展开收缩
			$('body').delegate('.jt', 'click', function() {
				var me=$(this);
				var data_time = $("#createTime").val();
				var start_time = $("#startTime").val();
				var end_time = $("#endTime").val();
				var time_type = $("#time_type").val();
				var ip_encode = $("#ip_encode").val();
				var app_encode = $("#app_encode").val();
				var low_times = $("#low_times").val();

				var finger_print = me.parent().parent().attr('data-id');
				var parent_order_nos = me.parent().parent().attr('parentordernos');
				var layer_no = parseInt(me.parent().parent().attr('layerno'));
				var nodeIndex = parseInt(me.parent().parent().attr('node-index'));

				var hasChild = me.parent().parent().parent().find('ul').length;
				if (hasChild == 0) {
					if (finger_print) {
						/*模拟请求数据 start*/
						/*var re = '<ul class="clearfix" node-index="10"><li data-id="327" style="text-indent:'+(nodeIndex+1)+'em'"><div class="col_0 col_item" ><a href="javascript:;" class="jt leaf"></a></div>' + '<div class="col_1 col_item">12123123</div><div class="col_2 col_item" ></div>' + '<div class="col_3 col_item">123123123真的吗真3真的吗真3真的吗真的吗真的啊</div><div class="col_4 col_item"></div><div class="col_5 col_item"><span class="proc-bar" style="width:20%"></span></div>' + '</li></ul>';
						$(this).parent().parent().after(re);
						$(this).attr('class', 'jt opened');*/
						/*模拟请求数据 end*/
						
						/*获取child*/
						$.get(subItemsUrl, {
							ip: ip_encode,
							app: app_encode,
							parentordernos: parent_order_nos,
							fingerprint: finger_print,
							layerno: layer_no + 1,
							nodeIndex: nodeIndex + 1,
							timeType: time_type,
							data_time: data_time,
							end_time: end_time,
							start_time: start_time,
							low_times: low_times
						}, function(re) {
							me.parent().parent().after(re);
							me.attr('class', 'jt opened');
						}, 'html');
					}
				} else {
					$(this).parent().parent().parent().find('ul').remove();
					$(this).attr('class', 'jt closed');
				}

			});

			//切换host
			$('body').delegate('.ips', 'click', function() {
				var load_url = Main.get_url($(this).attr('href_url'), false, true, false);
				//alert(load_url);
				window.location = load_url;
			});

			//表格降序
			$('body').delegate('.sortCol', 'click', function() {
				var load_url = Main.get_url($(this).parent().attr('href_url'), true, false, true) + "&orderType="+$(this).attr('order_type');
				//alert(load_url);
				window.location = load_url;
			});

			//切换页面
			$('body').delegate('.change_page', 'click', function() {
				var me = $(this);
				var load_url = Main.get_url($(this).parent().attr('href_url'), true, true, false)+"&page="+$(this).attr('page_index');
				//alert(load_url);
				window.location = load_url;
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
					dateFmt : 'yyyy-MM-dd HH:mm:ss'
				});
			});

			$("#endTime").on("click focus", function() {
				dtPicker.initByCfg({
					maxDate : $.formatDate(new Date(), 'yyyy-MM-dd'),
					dateFmt : 'yyyy-MM-dd HH:mm:ss'
				});
			});
		},

		get_url: function(base_url, same_host, same_order_type, same_page){
			var data_time = $("#createTime").val();
			var start_time = $("#startTime").val();
			var end_time = $("#endTime").val();
			var time_type = $("#time_type").val();
			var ip_encode = $("#ip_encode").val();
			var app_encode = $("#app_encode").val();
			var orderType = $("#order_type").val();
			var cur_page = $("#cur_page").val();
			var low_times = $("#low_times").val();

			var tp_url = base_url+"&start_time="+start_time+"&end_time="+end_time+"&data_time="+data_time+"&timeType="+time_type+"&low_times="+low_times;
			if(same_host){
				tp_url = tp_url+"&ip="+ip_encode+"&app="+app_encode;
			}
			if(same_order_type){
				tp_url = tp_url+"&orderType="+orderType;
			}
			if(same_page){
				tp_url = tp_url+"&page="+cur_page;
			}
			return tp_url;
		},
		/*sortColumn : function(sortCol, upFlag) {
			$.commonAjax({
				type : 'post',
				url : sortUrl,
				data : {
					sortCol : sortCol,
					upFlag : upFlag
				},
				success : function(re) {
					location.href = afterSort;
				},
				error : function(msg, status) {
					dialog.alert(msg);
				}
			});
		},*/

		initIcon : function() {
			var $jts = $('.jt');
			for (var i = 0; i < $jts.length; i++) {
				var $jt_itm = $($jts[i]);
				var isParent = $jt_itm.parent().parent().parent().find('ul').length;
				if (isParent == 0) {
					$jt_itm.attr('class', 'jt leaf');
				}
			}
		},

		// 处理分页页面跳转按钮
		pages : function() {
			$('#pageSubmit').click(function() {
				var pageIndexStr = $('#page').val();
				var maxNumber = $('#maxpage').val();
				var pageIndex = ~~pageIndexStr;
				if (pageIndexStr != pageIndex || pageIndexStr.indexOf(".") > -1) {
					alert('跳转页码必须为数值');
					$('#page').val("1");
					$('#page').focus();
					return false;
				} else if (pageIndex > ~~maxNumber) {
				    alert('跳转页码超过最大值，将查询最后一页：'+maxNumber);
					$('#page').val(maxNumber);
					pageIndex = ~~$('#page').val();//$('#page').focus();
					//return false;
				}
				if (pageIndex < 1) {
					pageIndex = 1;
				}

				window.location = Main.get_url($(this).parent().attr('href_url'), true, true, false)+"&page="+ pageIndex;
			});
		},
        //处理缩进
        initColor : function(obj) {
            var $node_ul=obj.parents().find('.child_ul');
            for (var i = 0; i < $node_ul.length; i++) {
                var $node_item=$($node_ul[$node_ul.length-1]);
                var node_index = $node_item.attr('node-index');
                var node_color=$node_item.attr('node-color');
                $node_item.width($node_item.width()-2*node_index);
                $node_item.css('backgroundColor',node_color);
            }
        }

	};
	Main.init();
});
