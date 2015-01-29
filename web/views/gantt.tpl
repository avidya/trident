<div id="gantDlg">
	<div id="treeMenu">
		<!--thead-->
		<div width="100%" class="tr_tit" id="tr_tit">
            <ul class="clearfix">
            % for item in viewmodel["tr_items"]:
                <li class="h-32 t{{item['tr_no']}}">
					{{item['tr_time']}}ms
				</li>
            % end
            </ul>
		</div>
		<ul class="tree_content clearfix ul_bg">
			<li class="clearfix">
				<div class="col_1 col_item">
					<div class="bar_warp1">
						<span class="proc-bar" style="width:80%;"></span>
						<cite class="pro-name">{{viewmodel['parent_url']}}</cite>
					</div>
				</div>
			</li>
			<ul class="child_ul clearfix">
                % for item_bar in viewmodel['sub_items']:
				<li class="clearfix" >
					<div class="col_1 col_item">
						<div class="zk" style="width:{{item_bar['left']}}px;"></div>
						<div class="bar_warp"  title="{{item_bar['url']}}">
							<span class="proc-bar" style="width:{{item_bar['middle']}}px;"></span>
							<cite class="pro-name">+d{{item_bar['d_time']}}+c{{item_bar['c_time']}}:{{item_bar['url']}}</cite>
						</div>
					</div>
				</li>
                % end
			</ul>
		</ul>
	</div>
</div>