%for item in viewmodle['rows']:
<ul class="child_ul clearfix" style="background:{{viewmodle['b_color']}}">
    <li data-id="{{item['audit_id']}}" node-index="{{viewmodle['node_index']}}" layerno="{{item['layer_no']}}" parentordernos="{{item['parent_order_nos']}}" class="clearfix">
        <div class="col_2 col_item" style="text-indent:{{viewmodle['text_indent']}}px;" title="{{item['url']}}"><a href="javascript:;" class="jt closed"></a>{{item['url']}}</div>
        <div class="col_3 col_item">{{item['attachments']}}</div>
        <div class="col_4 col_item"></div>
        <div class="col_5 col_item">{{item['create_time']}}</div>
        <div class="col_6 col_item" style="background:#fff;"><div class="bar_warp"><span class="proc-bar" style="width:{{item['elapse_bar']}}%;"><a class="GantBtn" title="点击查看时序" href="javascript:;">gantt</a></span></div><i class="pro_i">{{item['elapse']}}</i></div>
    </li>
</ul>
%end