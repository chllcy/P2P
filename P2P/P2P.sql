CREATE TABLE `p2p_info` (
  `p2pname` varchar(64) DEFAULT NULL COMMENT '����',
  `shortdesc` varchar(256) DEFAULT NULL COMMENT '�۸���Ϣ',
  `url` varchar(128) DEFAULT NULL,
  `star` varchar(64) DEFAULT NULL COMMENT '�Ǽ�',
  `longdesc` varchar(512) DEFAULT NULL,
  `jiaodan` varchar(32) DEFAULT NULL,
  `nianhua` varchar(32) DEFAULT NULL,
  `source` varchar(64) DEFAULT NULL COMMENT '��Դ',
  `insertdate` datetime DEFAULT NULL,
  `updatedate` datetime DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `zhijia` varchar(128) DEFAULT NULL,
  `tianyan` varchar(128) DEFAULT NULL,
  `rong360` varchar(128) DEFAULT NULL,
  KEY `p2p_info_name` (`p2pname`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8