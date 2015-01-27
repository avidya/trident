/**
 * 描述: 日期处理
 * 作者: 李洪波
 * 时间：2013年12月
 */
define(function(){

  var MONTH_NAMES = new Array('一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月', '1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月');
  var DAY_NAMES = new Array('星期天', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '周日','周一','周二','周三','周四','周五','周六');
  function LZ(x) { return (x < 0 || x > 9 ? "" : "0") + x }

  var datePlugin = {
    /* 判断是否日期 */
    isDate: function(val, format) {
      var date = $.getDateFromFormat(val, format);
      if (date == 0) { return false; }
      return true;
    },
    /* 日期比较 */
    compareDates: function (date1, date2) {
        var d1 = date1.getTime();
        var d2 = date2.getTime();
        if (d1 == 0 || d2 == 0) {
            return -1;
        }
        else if (d1 > d2) {
            return 1;
        }
        return 0;
    },
    /* 日期字符串比较 */
    compareDatesString: function (date1, dateformat1, date2, dateformat2) {
        var d1 = $.getDateFromFormat(date1, dateformat1);
        var d2 = $.getDateFromFormat(date2, dateformat2);
        if (d1 == 0 || d2 == 0) {
            return -1;
        }
        else if (d1 > d2) {
            return 1;
        }
        return 0;
    },
    /* 日期间隔 */
    dateDiff: function (interval, date1, date2) {
        var longl = date2.getTime() - date1.getTime(); //相差毫秒
        switch (interval.toLowerCase()) {
            case "y": return parseInt(date2.getFullYear() - date1.getFullYear());
            case "m": return parseInt((date2.getFullYear() - date1.getFullYear()) * 12 + (date2.getMonth() - date1.getMonth()));
            case "d": return parseInt(longl / 1000 / 60 / 60 / 24);
            case "w": return parseInt(longl / 1000 / 60 / 60 / 24 / 7);
            case "h": return parseInt(longl / 1000 / 60 / 60);
            case "n": return parseInt(longl / 1000 / 60);
            case "s": return parseInt(longl / 1000);
            case "l": return parseInt(longl);
        }
    },
    /* 重置日期的时分秒为0 */    
    clearTime: function(d) {
        d.setHours(0);
        d.setMinutes(0);
        d.setSeconds(0); 
        d.setMilliseconds(0);
        return d;
    },
    /* 拷贝日期 */
    cloneDate: function (d, dontKeepTime) {
        var me = this;
        if (dontKeepTime) {
            return $.clearTime(new Date(+d));
        }
        return new Date(+d);
    },    
    /* 加一个月 */
    addMonths: function (d, n, keepTime) {
        if (+d) {
            var m = d.getMonth() + n,
                check = $.cloneDate(d);
            check.setDate(1);
            check.setMonth(m);
            d.setMonth(m);
            if (!keepTime) {
                $.clearTime(d);
            }
            while (d.getMonth() != check.getMonth()) {
                d.setDate(d.getDate() + (d < check ? 1 : -1));
            }
        }
        return d;
    },
    /* 日期加减，可以设置是否保留时间 */
    addDays: function (d, n, keepTime) { // deals with daylight savings
        if (+d) {
            var dd = d.getDate() + n,
                check = $.cloneDate(d);
            check.setHours(9); // set to middle of day
            check.setDate(dd);
            d.setDate(dd);
            if (!keepTime) {
                $.clearTime(d);
            }
            while (d.getDate() != check.getDate()) {
                d.setTime(+d + (d < check ? 1 : -1) * HOUR_MS);
            }
        }
        return d;
    },
    /* 日期加减 */
    dateAdd: function (interval, number, date) {
        switch (interval.toLowerCase()) {
            case "y": return new Date(date.setFullYear(date.getFullYear() + number));
            case "m": return new Date(date.setMonth(date.getMonth() + number));
            case "d": return new Date(date.setDate(date.getDate() + number));
            case "w": return new Date(date.setDate(date.getDate() + 7 * number));
            case "h": return new Date(date.setHours(date.getHours() + number));
            case "n": return new Date(date.setMinutes(date.getMinutes() + number));
            case "s": return new Date(date.setSeconds(date.getSeconds() + number));
            case "l": return new Date(date.setMilliseconds(date.getMilliseconds() + number));
        }
    },
    /* 日期格式化，示例：$.formatDate(new Date(), "yyyy-MM-dd HH:mm:ss") */
    formatDate: function (date, format) {
        format = format + "";
        var result = "";
        var i_format = 0;
        var c = "";
        var token = "";
        var y = date.getYear() + "";
        var M = date.getMonth() + 1;
        var d = date.getDate();
        var E = date.getDay();
        var H = date.getHours();
        var m = date.getMinutes();
        var s = date.getSeconds();
        var yyyy, yy, MMM, MM, dd, hh, h, mm, ss, ampm, HH, H, KK, K, kk, k;
        // Convert real date parts into formatted versions
        var value = new Object();
        if (y.length < 4) { y = "" + (y - 0 + 1900); }
        value["y"] = "" + y;
        value["yyyy"] = y;
        value["yy"] = y.substring(2, 4);
        value["M"] = M;
        value["MM"] = LZ(M);
        value["MMM"] = MONTH_NAMES[M - 1];
        value["NNN"] = MONTH_NAMES[M + 11];
        value["d"] = d;
        value["dd"] = LZ(d);
        value["E"] = DAY_NAMES[E + 7];
        value["EE"] = DAY_NAMES[E];
        value["H"] = H;
        value["HH"] = LZ(H);
        if (H == 0) { value["h"] = 12; }
        else if (H > 12) { value["h"] = H - 12; }
        else { value["h"] = H; }
        value["hh"] = LZ(value["h"]);
        if (H > 11) { value["K"] = H - 12; } else { value["K"] = H; }
        value["k"] = H + 1;
        value["KK"] = LZ(value["K"]);
        value["kk"] = LZ(value["k"]);
        if (H > 11) { value["a"] = "PM"; }
        else { value["a"] = "AM"; }
        value["m"] = m;
        value["mm"] = LZ(m);
        value["s"] = s;
        value["ss"] = LZ(s);
        while (i_format < format.length) {
            c = format.charAt(i_format);
            token = "";
            while ((format.charAt(i_format) == c) && (i_format < format.length)) {
                token += format.charAt(i_format++);
            }
            if (value[token] != null) { result = result + value[token]; }
            else { result = result + token; }
        }
        return result;
    },
    /* 根据预定格式解析日期，示例：$.getDateFromFormat('2012-12-12 14:20:22', "yyyy-MM-dd HH:mm:ss"); */
    getDateFromFormat: function (val, format) {
        // Utility functions for parsing in getDateFromFormat()
        function _isInteger(val) {
            var digits = "1234567890";
            for (var i = 0; i < val.length; i++) {
                if (digits.indexOf(val.charAt(i)) == -1) { return false; }
            }
            return true;
        }
        function _getInt(str, i, minlength, maxlength) {
            for (var x = maxlength; x >= minlength; x--) {
                var token = str.substring(i, i + x);
                if (token.length < minlength) { return null; }
                if (_isInteger(token)) { return token; }
            }
            return null;
        }

        function getTimes(timeStr) {
            var obj = new Date($.getDateFromFormat(timeStr, "yyyy-MM-dd HH:mm:ss"));
            return obj.getTime();
        }

        val = val + "";
        format = format + "";
        var i_val = 0;
        var i_format = 0;
        var c = "";
        var token = "";
        var token2 = "";
        var x, y;
        var now = new Date();
        var year = now.getYear();
        var month = now.getMonth() + 1;
        var date = 1;
        var hh = now.getHours();
        var mm = now.getMinutes();
        var ss = now.getSeconds();
        var ampm = "";

        while (i_format < format.length) {
            // Get next token from format string
            c = format.charAt(i_format);
            token = "";
            while ((format.charAt(i_format) == c) && (i_format < format.length)) {
                token += format.charAt(i_format++);
            }
            // Extract contents of value based on format token
            if (token == "yyyy" || token == "yy" || token == "y") {
                if (token == "yyyy") { x = 4; y = 4; }
                if (token == "yy") { x = 2; y = 2; }
                if (token == "y") { x = 2; y = 4; }
                year = _getInt(val, i_val, x, y);
                if (year == null) { return 0; }
                i_val += year.length;
                if (year.length == 2) {
                    if (year > 70) { year = 1900 + (year - 0); }
                    else { year = 2000 + (year - 0); }
                }
            }
            else if (token == "MMM" || token == "NNN") {
                month = 0;
                for (var i = 0; i < MONTH_NAMES.length; i++) {
                    var month_name = MONTH_NAMES[i];
                    if (val.substring(i_val, i_val + month_name.length).toLowerCase() == month_name.toLowerCase()) {
                        if (token == "MMM" || (token == "NNN" && i > 11)) {
                            month = i + 1;
                            if (month > 12) { month -= 12; }
                            i_val += month_name.length;
                            break;
                        }
                    }
                }
                if ((month < 1) || (month > 12)) { return 0; }
            }
            else if (token == "EE" || token == "E") {
                for (var i = 0; i < DAY_NAMES.length; i++) {
                    var day_name = DAY_NAMES[i];
                    if (val.substring(i_val, i_val + day_name.length).toLowerCase() == day_name.toLowerCase()) {
                        i_val += day_name.length;
                        break;
                    }
                }
            }
            else if (token == "MM" || token == "M") {
                month = _getInt(val, i_val, token.length, 2);
                if (month == null || (month < 1) || (month > 12)) { return 0; }
                i_val += month.length;
            }
            else if (token == "dd" || token == "d") {
                date = _getInt(val, i_val, token.length, 2);
                if (date == null || (date < 1) || (date > 31)) { return 0; }
                i_val += date.length;
            }
            else if (token == "hh" || token == "h") {
                hh = _getInt(val, i_val, token.length, 2);
                if (hh == null || (hh < 1) || (hh > 12)) { return 0; }
                i_val += hh.length;
            }
            else if (token == "HH" || token == "H") {
                hh = _getInt(val, i_val, token.length, 2);
                if (hh == null || (hh < 0) || (hh > 23)) { return 0; }
                i_val += hh.length;
            }
            else if (token == "KK" || token == "K") {
                hh = _getInt(val, i_val, token.length, 2);
                if (hh == null || (hh < 0) || (hh > 11)) { return 0; }
                i_val += hh.length;
            }
            else if (token == "kk" || token == "k") {
                hh = _getInt(val, i_val, token.length, 2);
                if (hh == null || (hh < 1) || (hh > 24)) { return 0; }
                i_val += hh.length; hh--;
            }
            else if (token == "mm" || token == "m") {
                mm = _getInt(val, i_val, token.length, 2);
                if (mm == null || (mm < 0) || (mm > 59)) { return 0; }
                i_val += mm.length;
            }
            else if (token == "ss" || token == "s") {
                ss = _getInt(val, i_val, token.length, 2);
                if (ss == null || (ss < 0) || (ss > 59)) { return 0; }
                i_val += ss.length;
            }
            else if (token == "a") {
                if (val.substring(i_val, i_val + 2).toLowerCase() == "am") { ampm = "AM"; }
                else if (val.substring(i_val, i_val + 2).toLowerCase() == "pm") { ampm = "PM"; }
                else { return 0; }
                i_val += 2;
            }
            else {
                if (val.substring(i_val, i_val + token.length) != token) { return 0; }
                else { i_val += token.length; }
            }
        }
        // If there are any trailing characters left in the value, it doesn't match
        if (i_val != val.length) { return 0; }
        // Is date valid for month?
        if (month == 2) {
            // Check for leap year
            if (((year % 4 == 0) && (year % 100 != 0)) || (year % 400 == 0)) { // leap year
                if (date > 29) { return 0; }
            }
            else { if (date > 28) { return 0; } }
        }
        if ((month == 4) || (month == 6) || (month == 9) || (month == 11)) {
            if (date > 30) { return 0; }
        }
        // Correct hours value
        if (hh < 12 && ampm == "PM") { hh = hh - 0 + 12; }
        else if (hh > 11 && ampm == "AM") { hh -= 12; }
        var newdate = new Date(year, month - 1, date, hh, mm, ss);
        return newdate.getTime();
    },
    /* 直接解析日期，示例：$.parseDate('2013-7-15') */
    parseDate: function (val) {
        var preferEuro = (arguments.length == 2) ? arguments[1] : false;
        generalFormats = new Array('y-M-d', 'MMM d, y', 'MMM d,y', 'y-MMM-d', 'd-MMM-y', 'MMM d');
        monthFirst = new Array('M/d/y', 'M-d-y', 'M.d.y', 'MMM-d', 'M/d', 'M-d');
        dateFirst = new Array('d/M/y', 'd-M-y', 'd.M.y', 'd-MMM', 'd/M', 'd-M');
        var checkList = new Array('generalFormats', preferEuro ? 'dateFirst' : 'monthFirst', preferEuro ? 'monthFirst' : 'dateFirst');
        var d = null;
        for (var i = 0; i < checkList.length; i++) {
            var l = window[checkList[i]];
            for (var j = 0; j < l.length; j++) {
                d = $.getDateFromFormat(val, l[j]);
                if (d != 0) { return new Date(d); }
            }
        }
        return null;
    }
  };

  $.extend(datePlugin);

});