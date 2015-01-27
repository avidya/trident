DROP TABLE IF EXISTS trident_audit;
--消息记录详情表
CREATE TABLE trident_audit
(
  audit_id serial NOT NULL,
  root_audit_id integer NOT NULL,                 --根节点id
  parent_audit_id integer NOT NULL,               --父节点id，0表示顶层记录
  hostname character varying(50) NOT NULL,        --主机名
  ip character varying(100) NOT NULL,             --ip地址
  app character varying(100) NOT NULL,            --应用名
  ip_encode character varying(40) NOT NULL,       --ip地址 md5
  app_encode character varying(40) NOT NULL,      --应用名 md5
  async character varying(20) NOT NULL,           --异步或同步调用
  url character varying(800) NOT NULL,            --函数调用的方法
  attachments character varying(800),             --函数调用方法时传送的参数
  begin_time bigint NOT NULL,                     --函数调用开始时间
  end_time bigint NOT NULL,                       --函数调用结束时间
  durable_time integer NOT NULL,                  --函数调用所花时长
  success character varying(6) NOT NULL,          --函数调用成功与否
  layer_no  integer NOT NULL,                     --在函数调用链上的层次编号
  order_no  integer NOT NULL,                     --在同一层次上的序号
  parent_order_nos character varying(500)  NOT NULL,   --上一层次的order，格式为 上层-上层-上层......
  finger_print character varying(64) NOT NULL DEFAULT ''::character varying,    --改函数调用所在的指纹
  create_time timestamp with time zone NOT NULL DEFAULT now(),    --信息采集的时间
  CONSTRAINT pk_trident_audit PRIMARY KEY (audit_id)
);

CREATE INDEX i_trident_audit_root_audit_id
  ON trident_audit
  USING btree
  (root_audit_id);

CREATE INDEX i_trident_audit_finger_print_layer_order
  ON trident_audit
  USING btree
  (finger_print, layer_no, order_no);

CREATE INDEX i_trident_audit_ip_encode
   ON trident_audit
   USING btree
   (ip_encode);

CREATE INDEX i_trident_audit_app_encode
   ON trident_audit
   USING btree
   (app_encode);

DROP TABLE IF EXISTS trident_audit_finger;
CREATE TABLE trident_audit_finger
(
    date_time integer NOT NULL,                   --函数调用所在的日期
    finger_print character varying(64) NOT NULL,  --函数调用的指纹
    url character varying(800) NOT NULL,          --函数调用名称
    times integer NOT NULL,                       --记录的次数
    durable_time_avg integer NOT NULL,            --记录的平均调用时间
    ip_encode character varying(40) NOT NULL,     --ip地址 md5
    app_encode character varying(40) NOT NULL,    --应用名 md5
    create_time timestamp with time zone NOT NULL DEFAULT now(),    --信息采集的时间
    CONSTRAINT pk_trident_audit_finger_date_time_finger_print PRIMARY KEY (date_time, finger_print)
);

CREATE INDEX i_trident_audit_finger_ip_encode
   ON trident_audit_finger
   USING btree
   (ip_encode);

CREATE INDEX i_trident_audit_finger_app_encode
   ON trident_audit_finger
   USING btree
   (app_encode);


-- 指纹记录表， 每天每个指纹一条
DROP TABLE IF EXISTS trident_audit_ip;
--产生消息的主机ip和app对应关系表
CREATE TABLE trident_audit_ip
(
	audit_ip character varying(16) NOT NULL,
	audit_ip_encode character varying(40) NOT NULL,
  audit_app_encode character varying(40) NOT NULL,
  host_name character varying(50),
	CONSTRAINT pk_trident_audit_ip PRIMARY KEY (audit_ip_encode, audit_app_encode)
);

DROP TABLE IF EXISTS trident_audit_app;
--产生消息的app表
CREATE TABLE trident_audit_app
(
	audit_app character varying(100) NOT NULL,
	audit_app_encode character varying(40) NOT NULL,
	CONSTRAINT pk_trident_audit_app PRIMARY KEY (audit_app_encode)
);
