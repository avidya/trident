/**
 * 工具模块
 * @author luoweiping
 * @version 2014-07-24
 * @since 2013-07-04
 */
define(function(require, exports, module) {
	function Util() {

	}
	/********************************/
	/*       Some Useful Plugin     */
	/********************************/
	$.extend({
		/* the latest common ajax call */
		commonAjax : function(options) {
			var url = options.url;
			if (!url) {
				alert('Ajax接口地址为空！');
				return;
			}
			var defaults = {
				type : 'get',
				dataType : 'json',
				async : true,
				cache : false
			};
			var settings = $.extend(defaults, options);
			settings.success = function(re, textStatus, xhr) {
				if (re.status === 0) {
					options.success(re.data);
				} else {
					if (options.error) {
						options.error(re.errorMsg || '操作失败！', re.status);
					}
				}
			};
			settings.error = function(xhr, status, handler) {
				if (options.error) {
					options.error('操作失败！', 1);
				}
			};
			$.ajax(settings);
		}
	});
	module.exports = Util;
});
