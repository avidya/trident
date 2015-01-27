/**
 * My97DatePicker
 * User: 张顺金 <zhangshunjin@eetop.com>
 * Date: 13-7-17 下午5:07
 */
define(function(require, exports, module) {
    var WdatePicker = require("lib/datePicker/src/WdatePicker");

    function DatePicker() {}

    DatePicker.prototype.init = function() {
        WdatePicker({
            dateFmt: 'yyyy-MM-dd'
        });
    };

    DatePicker.prototype.initByFmt = function(fmtStr) {
        WdatePicker({
            isShowOK: false,
            isShowToday: false,
            isShowClear: false,
            highLineWeekDay: false,
            isShowOthers: false,
            qsEnabled: false,
            dateFmt: fmtStr
        });
    };

    DatePicker.prototype.initByCfg = function(cfgObj) {
        if(typeof cfgObj === undefined){
            cfgObj = {};
        }
        cfgObj = $.extend({
            isShowOK: false,
            isShowToday: false,
            isShowClear: false,
            highLineWeekDay: false,
            isShowOthers: false,
            qsEnabled: false,
            dateFmt: 'yyyy-MM-dd'
        }, cfgObj);

        WdatePicker(cfgObj);
    };

    module.exports = DatePicker;
});