# coding:utf8
import sqlite3
import requests
import re
import time
import logging
import sys

from sqlite3 import DatabaseError


class duotooImage:

    allTags = [{'text':'大自然','tag':'daziran'}, {'text':'腿模美女,台湾腿模,腿模图片','tag':'tuimo'}, {'text':'骨感美女,骨感美女图片,骨感模特','tag':'gugan'},
               {'text':'个性','tag':'gexing'}, {'text':'宋-KiKi写真图片,模特宋七七简介资料,丰满巨乳美女宋-KiKi高清私房套图','tag':'songqiqi'},
               {'text':'鲤鱼纹身','tag':'liyuwenshen'}, {'text':'梨儿Lace','tag':'lierLace'}, {'text':'好身材美女,魔鬼身材,完美身材,身材好的美女图片','tag':'haoshencai'},
               {'text':'姐妹','tag':'jiemei'}, {'text':'小热巴美女图片,小琪迪依简介资料,宅男女神小热巴高清写真套图','tag':'xiaoreba'},
               {'text':'妩媚女人,妩媚美女图片','tag':'mei'}, {'text':'恶搞','tag':'egao'}, {'text':'mm图片,大胸mm,美女MM,性感mm,mm写真,mm美女图片','tag':'mm'},
               {'text':'李梦婷图片,李梦婷简介资料,李梦婷高清写真大全','tag':'limegnting'}, {'text':'Cheryl青树写真图片,平面模特孙梦怡简介资料,Cheryl青树高清套图全集','tag':'qingshu'},
               {'text':'卡哇伊','tag':'kawayi'}, {'text':'丁筱南图片,丁筱南简介资料,御姐丁筱南巨乳肥臀写真','tag':'dingyounan'},
               {'text':'美味','tag':'meiwei'}, {'text':'晓茜sunny写真图片,莫晓茜夹豆妹简介资料,Showgirl模特晓茜高清套图大全','tag':'xiaoqian'},
               {'text':'推女神','tag':'tuinvshen'}, {'text':'性感女神,宅男女神,克拉女神','tag':'nvshen'},
               {'text':'黄歆苑Chobits图片,歆小兔简介资料,性感川妹子黄歆苑高清写真套图','tag':'huangxinyuan'},
               {'text':'欧美人体艺术,欧美女优,欧美人体艺术摄影,西西人体欧美人体写真,美国人体艺术,外国人体艺术','tag':'oumeirenti'},
               {'text':'陈小梨','tag':'chenxiaoli'}, {'text':'混血美女,混血宝贝,混血mm','tag':'hunxue'}, {'text':'迷人','tag':'miren'},
               {'text':'嫩模写真,嫩模图片','tag':'nenmo'}, {'text':'蝴蝶纹身','tag':'hudiewenshen'}, {'text':'长发,长发美女,长发图片','tag':'changfa'},
               {'text':'捆绑美女,sm捆绑,丝袜捆绑,捆绑美女图片,亚洲捆绑调教,捆绑绳艺艺术,制服捆绑女警','tag':'kunbang'},
               {'text':'长裙美女,连衣长裙,抹胸长裙图片,长裙美女图片','tag':'changqun'}, {'text':'刺青','tag':'ciqing'},
               {'text':'萌汉药大尺度写真,模特萌汉药简介资料,头条女神萌汉药高清写真套图','tag':'megnhanyao'}, {'text':'日本学生妹,性感学生妹,清纯学生妹,可爱学生妹','tag':'xueshengmei'},
               {'text':'妹妹人体艺术,窝窝妺妺人体艺术,666人体艺术','tag':'meimeirentiyishu'}, {'text':'风骚美女,风骚少妇,风骚女人,风骚熟女老师,风骚护士诱惑','tag':'fengsao'},
               {'text':'沈梦瑶图片,沈梦瑶简介资料,沈梦瑶高清写真套图全集','tag':'shenmengyao'}, {'text':'冷艳美女,高贵冷艳','tag':'lengyan'},
               {'text':'沐若昕美女图片,美乳模特沐若昕简介资料,沐若昕高清写真套图','tag':'muruoxin'}, {'text':'推女郎,tuigirl推女郎官网,无圣光','tag':'tuinvlang'},
               {'text':'鸽子血','tag':'gezixue'}, {'text':'狗狗','tag':'gougou'}, {'text':'比基尼美女,比基尼美女图片,性感比基尼写真','tag':'bijini'},
               {'text':'欧美图片,欧美美女,欧美美女图片,欧美女人','tag':'oumei'}, {'text':'妲己Toxic图片,妲己Toxic柠檬c_lemon简介资料,狐媚女神妲己Toxic写真套图','tag':'dajitoxic'},
               {'text':'ppt','tag':'ppt'}, {'text':'美女人体艺术图片,美女人体艺术写真,美女人体艺术摄影','tag':'meinvrenti'},
               {'text':'大尺度美女图片,国模大尺度,大尺度私拍,尺度极大的图片,熟妇大尺度人体艺术','tag':'dachidu'},
               {'text':'美女模特,性感模特,平面模特,商务模特,泳装模特图片,中国模特写真','tag':'mote'}, {'text':'少女,少女图片,清纯美少女,90后少女','tag':'shaonv'},
               {'text':'日本人体,日本人体艺术,日本人体艺术图片,大胆日本人体','tag':'ribenrenti'}, {'text':'刘飞儿faye图片,刘飞儿无光圣图大理写真,刘飞儿简介资料','tag':'liufeier'},
               {'text':'美臀,性感美臀,美女美臀,美臀诱惑图片','tag':'meitun'}, {'text':'谢芷馨Sindy美女图片,绯月樱Cherry简介资料,国模谢芷馨超高清写真套图','tag':'xiezhixin'},
               {'text':'韩子萱人体写真,嫩模韩子萱简介资料,韩子萱大胆内衣高清套图','tag':'hanzixuan'}, {'text':'半甲纹身','tag':'banjiawenshen'},
               {'text':'许诺Sabrina图片,许诺Sabrina简介资料,女神许诺Sabrina高清写真套图','tag':'xunuo'}, {'text':'御姐图片,御姐控,巨乳御姐,萝莉御姐,御姐美女高清写真图片','tag':'yujie'},
               {'text':'空姐图片,性感空姐,空姐丝袜,空姐制服','tag':'kongjie'}, {'text':'可爱图片,可爱手机壁纸,可爱女人,小可爱图片,可爱美女','tag':'keai'},
               {'text':'美女私房照,私人拍摄,私人摄影,美女私密写真集,私密图库','tag':'sifang'}, {'text':'淼淼王淼图片,王淼简介资料,淼淼萌萌哒超高清写真套图','tag':'miaomiao'},
               {'text':'气质美女,气质美女生活照,短发气质美女','tag':'qizhi'}, {'text':'亚洲人体艺术,亚洲美女写真,亚洲mm,亚洲美图,亚洲自拍偷拍图片','tag':'yazhourenti'},
               {'text':'文字','tag':'wenzi'}, {'text':'龙纹身','tag':'longwenshen'},
               {'text':'美女诱惑,丝袜诱惑,制服诱惑,性感美女诱惑,少妇诱惑,巨乳翘臀诱惑,美臀熟女诱惑,美腿诱惑写真图片','tag':'youhuo'},
               {'text':'gogo人体艺术,大胆人gogo体艺术,国模gogo大胆高清网站,GOGO人体高清人体,gogo人体美鮑图片','tag':'gogorentiyishu'},
               {'text':'柳侑绮图片,柳侑绮写真高清全集,柳侑绮简介资料','tag':'liuyouqi'}, {'text':'优星馆','tag':'youxingguan'},
               {'text':'王梓童doirs图片,王梓童个人简介资料,模特王梓童doirs超高清写真套图全集','tag':'wangxintong'}, {'text':'雪景','tag':'xuejing'},
               {'text':'情趣内衣,情趣内衣美女','tag':'qingquneiyi'}, {'text':'风韵少妇,成熟风韵,风韵犹存,风韵女人','tag':'fengyun'},
               {'text':'丁字裤,丁字裤美女,性感丁字裤','tag':'dingziku'}, {'text':'插画','tag':'chahua'}, {'text':'rosi写真','tag':'Rosi'},
               {'text':'女神卓娅祺图片,翘臀美女卓娅祺简介资料,兔子NINA高清写真套图','tag':'zhuoyaqi'}, {'text':'顾欣怡图片,顾欣怡简介资料,美女模特顾欣怡高清写真','tag':'guxinyi'},
               {'text':'赵伊彤高清写真图片,推女郎模特赵伊彤冷月liyi简介资料','tag':'zhaoyitong'}, {'text':'黑丝美女,黑丝诱惑,黑丝少妇,黑丝高跟','tag':'heisi'},
               {'text':'创意','tag':'chuangyi'}, {'text':'aiss爱丝,AISS爱丝官网,丝袜美女高清写真套图','tag':'aissaisi'}, {'text':'背部纹身','tag':'beibuwenshen'},
               {'text':'雨天','tag':'yutian'}, {'text':'蜜桃社','tag':'mitaoshe'}, {'text':'苏可er写真图片,模特苏可儿简介资料,苏可可人体艺术套图','tag':'sukeke'},
               {'text':'女主播','tag':'nvzhubo'}, {'text':'美胸美女,美胸图片,美胸模特','tag':'meixiong'}, {'text':'叶佳颐美女图片,叶小渼简介资料,模特叶佳颐高清写真套图','tag':'yejiayi'},
               {'text':'手臂','tag':'shoubi'}, {'text':'短发美女,短发图片,短发女神','tag':'duanfa'}, {'text':'紧身裤美女,紧身牛仔裤美女,紧身内衣图片,紧身牛仔,紧身美臀','tag':'jinshen'},
               {'text':'美女套图,无圣光套图,精品套图超市,人体艺术套图,欧美亚洲套图下载,美女写真套图','tag':'taotu'}, {'text':'非主流','tag':'feizhuliu'},
               {'text':'少女人体艺术,西西人体艺少女人体,少女人体艺术图片,美少女人体艺术','tag':'shaonvrentiyishu'}, {'text':'婕西儿图片,婕西儿简介资料,婕西儿写真套图','tag':'jiexier'},
               {'text':'小清新美女,小清新图片,小清新壁纸,清新美女图片','tag':'xiaoqingxin'}, {'text':'热裤美女,街拍热裤,超短热裤,美女热裤,牛仔热裤mm','tag':'reku'},
               {'text':'Yumi尤美图片,Ann尤美简介资料,淘女郎Yumi尤美高清写真','tag':'youmeiyumi'}, {'text':'夜景','tag':'yejing'},
               {'text':'牛仔裤美女,紧身牛仔裤美女,比基尼牛仔裤,牛仔裤美臀图片','tag':'niuziku'}, {'text':'甜美美女,甜美女孩,甜美女生,甜美少女','tag':'tianmei'},
               {'text':'芝芝Booty美女图片,模特陈芝资料简介,花椒女主播芝芝Booty超高清写真套图','tag':'zhizhibooty'}, {'text':'气球','tag':'qiqiu'},
               {'text':'大波美女,大波妹,大波霸,大波MM,性感丰满大波美女图片','tag':'dabomeinv'}, {'text':'冷不丁图片,丰满巨乳美少女冷不丁简介资料,冷不丁高清写真套图大全','tag':'lengbuding'},
               {'text':'伤感','tag':'shanggan'}, {'text':'萌琪琪图片,萌琪琪简介资料,嫩模萌琪琪Irene写真套图全集','tag':'mengqiqi'},
               {'text':'高跟美女,高跟美腿,高跟丝袜,高跟控','tag':'gaogenxie'}, {'text':'女生图片,女生照片,可爱女生图片,唯美女生图片,粉嫩小女生,性感女生','tag':'nvsheng'},
               {'text':'美媛馆','tag':'meiguan'}, {'text':'猫咪','tag':'mao'}, {'text':'','tag':''}, {'text':'大胸美女,大胸mm,大胸妹子,大胸美女图片,性感大胸美女,大胸女人照片','tag':'daxiong'},
               {'text':'乳沟美女,少妇乳沟,乳沟诱惑','tag':'rugou'}, {'text':'嗲囡囡','tag':'dianannan'}, {'text':'湿身图片,美女湿身','tag':'shishen'},
               {'text':'男生','tag':'nansheng'}, {'text':'旗袍美女,旗袍图片,性感旗袍诱惑,旗袍美女图片,旗袍丝袜','tag':'qipao'}, {'text':'个性纹身','tag':'gexingwenshen'},
               {'text':'尤物,性感尤物,勾魂尤物,天生尤物,美女尤物','tag':'youwu'}, {'text':'魅妍社,魅妍社美女','tag':'she'},
               {'text':'艾小青写真集,嫩模艾小青简介资料,艾小青美腿制服写真','tag':'aixiaoqing'}, {'text':'和服美女,日本和服图片','tag':'hefu'},
               {'text':'丽柜美女,丽柜图片,丽柜丝袜,丽柜套图','tag':'ligui'}, {'text':'穆菲菲写真图片,魏飞霞angela简介资料,美女穆菲菲大胆内衣套图','tag':'mufeifei'},
               {'text':'李可可写真图片,巨乳美女李可可简介资料,秀人模特李可可高清套图全集','tag':'likeke'}, {'text':'beautyleg,beautyleg腿模写真套图,beautyleg美腿丝袜图片','tag':'beautyleg'},
               {'text':'空间','tag':'kongjian'}, {'text':'Evelyn艾莉图片,美女模特evelyn艾莉大尺度写真套图全集','tag':'evelyn'},
               {'text':'巨乳美女,童颜巨乳美女,巨乳波霸,巨乳诱惑,欧美巨乳,巨乳人体艺术','tag':'juru'},
               {'text':'裸体艺术,美女裸体艺术,美女裸体图片,美女裸图,女性裸身照片,全裸美女,裸身美女,美女裸体写真,美女裸体照片','tag':'luoti'},
               {'text':'肉丝美女,肉丝美腿,肉丝高跟,肉丝袜诱惑,肉丝吧,性感肉丝空姐','tag':'rousi'}, {'text':'熟女图片,日本熟女少妇,淫荡熟女人妻,老熟女吧,熟女诱惑','tag':'shunv'},
               {'text':'星空','tag':'xingkong'}, {'text':'萌妹子图片,妹子网,软妹子,嫩妹子,妹子图','tag':'mengmeizi'}, {'text':'浪漫','tag':'langman'},
               {'text':'绮里嘉图片,美女绮里嘉高清写真套图','tag':'lijia'}, {'text':'治愈系','tag':'zhiyuxi'}, {'text':'佟蔓性感大胸图片,馨蕊佟蔓简介资料,丰满美女佟蔓大胆写真套图','tag':'tongman'},
               {'text':'黑白','tag':'heibai'}, {'text':'秀人网写真图片,秀人网高清套图全集','tag':'xiurenwang'},
               {'text':'蔡文钰angle图片,模特主播蔡文钰简介资料,樱桃小嘴儿高清写真套图全集','tag':'caiwenyu'}, {'text':'尤果网,尤果网美女写真','tag':'youguowang'},
               {'text':'王馨瑶写真集,嫩模王馨瑶简介资料,王馨瑶美腿高清套图','tag':'wangxinyao'}, {'text':'菠萝社,兔几盟写真,萝luoli社,萝莉吧,BoLoli波萝社','tag':'boluoshe'},
               {'text':'心妍小公主(李妍曦)写真图片,御姐女神李妍曦简介资料,巨乳肥臀高清套图','tag':'xinyan'}, {'text':'酥胸美女,酥胸诱惑,酥胸写真','tag':'suxiong'},
               {'text':'梓萱Crystal图片,梓萱简介资料,推女神梓萱Crystal写真套图','tag':'zixuan'}, {'text':'彩色纹身','tag':'caisewenshen'}, {'text':'秋天','tag':'qiutian'},
               {'text':'林美惠子Mieko图片,林美惠子简介资料,林美惠子大尺度内衣写真套图','tag':'linmeihuizi'}, {'text':'90后,90后美女,90后女优,90后清纯美女图片','tag':'90hou'},
               {'text':'莲花','tag':'lianhua'}, {'text':'顶级人体艺术,天天人体艺术','tag':'dingjirentiyishu'}, {'text':'女仆,女仆装,性感女仆','tag':'nvpu'},
               {'text':'程彤颜图片,程彤颜简介资料,TGOD推女神程彤颜Gin写真套图','tag':'chengtongyan'}, {'text':'国模王婉悠巨乳图片,王格简介资料,王婉悠爆乳大尺度高清写真套图','tag':'wangwanyou'},
               {'text':'小九vin写真图片,推女神模特小九vin简介资料,小九vin高清套图大全','tag':'xiaojiuwin'},
               {'text':'大奶美女,大奶子美女,大奶妹,大奶头,大奶女人,欧美大奶,大奶奶美女,大奶人体艺术','tag':'danai'}, {'text':'复古','tag':'fugu'},
               {'text':'尤物馆,尤物网','tag':'youwuguan'}, {'text':'豹纹图片,豹纹内衣,豹纹丝袜,豹纹诱惑','tag':'baowen'},
               {'text':'性感人体艺术,欧美性感人体艺术,女性人体艺术','tag':'xingganrentiyishu'}, {'text':'赵小米Kitty图片,模特赵小米简介资料,美女赵小米写真套图大全高清','tag':'zhaoxiaomi'},
               {'text':'制服,制服美女,制服诱惑,情趣制服','tag':'zhifu'}, {'text':'帅气','tag':'shuaiqi'},
               {'text':'思淇Sukiii图片,思淇Sukiii简介资料,模特美女思淇Sukiii私房写真套图','tag':'siqisukiii'}, {'text':'背影','tag':'beiying'},
               {'text':'模范学院','tag':'mofanxueyuan'}, {'text':'丰满美女,丰满少妇,丰满人体艺术','tag':'fengmanrenti'},
               {'text':'孙梦瑶美女图片,孙梦瑶简介资料,长腿模特孙梦瑶高清写真套图','tag':'sunmengyao'}, {'text':'护士美女,护士制服,性感护士装,丝袜护士图片','tag':'hushi'},
               {'text':'浴室美女,浴室美女图片,浴室人体写真,浴室美女湿身图','tag':'yushi'}, {'text':'超短裙美女,齐b小短裙,性感短裙美女,短裙mm','tag':'duanqun'},
               {'text':'周妍希写真图片,土肥圆矮挫穷周妍希资料简介,性感尤物周妍希高清套图','tag':'zhouyanxi'}, {'text':'飞图网,飞图网美女图片,飞图网官网模特写真原版高清套图全集','tag':'feituwang'},
               {'text':'可乐Vicky图片,可乐Vicky简介资料,推女神模特可乐Vicky高清写真','tag':'kelevicky'}, {'text':'惊艳','tag':'jingyan'}, {'text':'白嫩,白嫩美女,丰满白嫩','tag':'bainen'},
               {'text':'萝莉图片,巨乳萝莉,日本萝莉,萝莉吧','tag':'luoli'}, {'text':'杨晨晨图片,杨晨晨简介资料,爱蜜社模特sugar小甜心CC高清写真套图','tag':'yangchenchen'},
               {'text':'周于希写真图片,小狐狸dummy简介资料,平面模特周于希高清写真套图','tag':'zhouyuxi'}, {'text':'李雪婷Anna图片,大乳美女李雪婷简介资料,李雪婷超高清写真套图','tag':'lixueting'},
               {'text':'夏小秋秋图片,夏小秋秋秋简介资料,内衣模特夏小秋秋性感写真套图','tag':'xiaxiaoqiuqiu'}, {'text':'自拍','tag':'zipai'},
               {'text':'美女校花,大学校花图片,清纯校花','tag':'xiaohua'}, {'text':'温心怡写真,尤果网性感模特温心怡简介资料,温心怡高清图片大全','tag':'wenxinyi'},
               {'text':'黄乐然写真图片,妮小妖黄楽然简介资料,黄楽然美乳翘臀大胆写真','tag':'huangleran'}, {'text':'阿宝色','tag':'abaose'},
               {'text':'透视装图片,性感透视装,透视装诱惑','tag':'toushizhuang'}, {'text':'意境','tag':'yijing'}, {'text':'美乳图片,美女美乳,极品美乳','tag':'meiru'},
               {'text':'时尚人体艺术,360人体艺术,女人人体艺术','tag':'shishangrentiyishu'}, {'text':'霸气','tag':'baqi'}, {'text':'山水','tag':'shanshui'}, {'text':'动漫','tag':'dongman'},
               {'text':'大胆人体,大胆人体艺术,大胆人体写真图片','tag':'dadanrenti'}, {'text':'于姬una写真图片,模特于姬资料简介,女神于姬高清套图全集','tag':'yuji'},
               {'text':'肥臀少妇,丰乳肥臀,肥臀少女','tag':'feitun'}, {'text':'时尚','tag':'shishang'}, {'text':'夕阳','tag':'xiyang'},
               {'text':'美女车模,性感车模写真,车模图片,车模走光,车模壁纸','tag':'chemo'}, {'text':'美腿美女,大长腿美女,性感美腿,美腿图片,大白腿','tag':'meitui'},
               {'text':'女优,日本女优,av女优大全','tag':'nvyou'}, {'text':'傲娇萌萌写真图片,周大萌简介资料,k8傲娇萌萌Vivian高清套图大全','tag':'mengmeng'},
               {'text':'头条女神图片,TouTiao头条女神官网高清写真套图全集','tag':'toutiaonvshen'}, {'text':'邹晶晶图片,邹晶晶个人简介资料,车模邹晶晶大尺度高清写真','tag':'zoujingjing'},
               {'text':'琳琳ailin图片,小沫琳简介资料,模特琳琳ailin高清写真全集','tag':'xiaomolin'}, {'text':'松果儿图片,闫雪松松果儿简介资料松果儿无圣光高清写真大全','tag':'songguoer'},
               {'text':'易阳写真图片,易阳Silvia简介资料,巨乳大胸美女易阳超高清套图','tag':'yiyang'}, {'text':'王雨纯人体图片,王语纯简介资料,王语纯高清写真集套图','tag':'wangyuchun'},
               {'text':'人体模特,人体欣赏,人体写真,裸体模特,平面模特,人体艺术模特写真,西西人体模特','tag':'rentimote'},
               {'text':'唐琪儿图片,麋妹唐琪儿简介资料,唐琪儿Beauty高清写真套图','tag':'tangqier'}, {'text':'古风','tag':'gufeng'},
               {'text':'顶级少妇,性感少妇图片,风骚少妇,丝袜少妇诱惑,熟女少妇,丰满少妇,日本少妇系列','tag':'shaofu'}, {'text':'亲吻','tag':'qinwen'},
               {'text':'熊吖BOBO图片,熊吖BOBO简介资料,淘女郎模特熊吖bobo高清写真套图全集','tag':'xiongya'}, {'text':'特色','tag':'tese'}, {'text':'颓废','tag':'tuifei'},
               {'text':'妖娆美女,妖娆图片,妖娆美女图片','tag':'yaorao'}, {'text':'白领丽人,白领美女','tag':'bailing'},
               {'text':'刘钰儿图片,刘钰儿简介资料,模特刘钰儿高清写真大全','tag':'liuyuer'},
               {'text':'中国人体艺术,最大胆的中国人体艺术,中国人体艺术网,中国人体模特,中国人体艺术摄影图片','tag':'zhongguorenti'},
               {'text':'大屁股美女,大屁股女人,美女屁股,雪白的屁股,美女屁屁','tag':'dapigumeinv'}, {'text':'绮梦Cherish图片,绮梦简介资料,推女神模特绮梦Cherish写真套图','tag':'qimeng'},
               {'text':'低胸装美女,低胸诱惑,低胸写真','tag':'dixiong'}, {'text':'图腾','tag':'tuteng'}, {'text':'粉嫩美女,粉嫩小女生,粉嫩小妹,粉嫩学生妹,粉嫩美眉,极品粉嫩鲍鱼','tag':'fennen'},
               {'text':'lomo','tag':'lomo'}, {'text':'森系','tag':'senxi'}, {'text':'拥抱','tag':'yongbao'}, {'text':'韩国人体艺术,韩国人体模特,韩国人体艺术图片','tag':'hanguorenti'},
               {'text':'米妮大萌萌美女图片,童颜巨乳米妮大萌萌写真套图','tag':'minidameng'}, {'text':'大胆,大胆美女,大胆模特写真','tag':'dadan'}, {'text':'牵手','tag':'qianshou'},
               {'text':'蕾丝美女,蕾丝猫,蕾丝丝袜,蕾丝内衣,蕾丝兔宝宝,蕾丝诱惑,蕾丝情趣内衣','tag':'leisi'}, {'text':'热辣美女,火爆美女,火辣内衣,火辣图片,火辣女孩,火辣美女图片','tag':'huola'},
               {'text':'翘臀美女,性感翘臀诱惑,翘臀美女图片','tag':'qiaotun'}, {'text':'落叶','tag':'luoye'}, {'text':'半裸美女,半裸尤物,半裸模特,半裸写真,半裸诱惑,半裸人体艺术','tag':'banluo'},
               {'text':'玛鲁娜翘臀图片,非诚勿扰女嘉宾汤曼玲简介资料,秀人网玛鲁娜超高清大胆写真套图','tag':'maluna'},
               {'text':'苏子淇写真图片,苏子淇简介资料,美女模特苏子淇高清写真套图','tag':'suziqi'}, {'text':'海边','tag':'haibian'}, {'text':'俏皮','tag':'qiaopi'},
               {'text':'童颜美女,童颜巨乳美女,童颜巨胸,童颜乳神','tag':'tongyan'}, {'text':'尤妮丝图片,肉蛋妹尤妮丝简介资料,egg尤妮丝写真套图','tag':'younisi'},
               {'text':'爆乳美女,爆乳美女写真,爆乳女优,爆乳mm,爆乳肉感大码av在线','tag':'baoru'}, {'text':'护眼','tag':'huyan'}, {'text':'白皙美女','tag':'bai'},
               {'text':'爱蜜社','tag':'aimishe'}, {'text':'美女秘书,性感女秘书,丝袜秘书','tag':'mishu'}, {'text':'嫩模月音瞳图片,月音瞳简介资料,童颜巨乳网红月音瞳高清写真套图','tag':'yueyintong'}]

    domainUrl = "https://www.duotoo.com"
    tagUrl = domainUrl + "/tag"
    categoryUrls = ("http://www.duotoo.com/xingganmeinv/", "http://www.duotoo.com/waiguomeinv/", "http://www.duotoo.com/siwameinv/",
                    "http://www.duotoo.com/meinvxiezhen/", "http://www.duotoo.com/rentiyishu/", "http://www.duotoo.com/neiyimeinv/",
                    "http://www.duotoo.com/qingchunmeinv/", "http://www.duotoo.com/meinvmingxing/","http://www.duotoo.com/changtuimeinv/")


    def __init__(self):
        self.create_tables()

    def __httpHeader(self):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "cookie": "Hm_lvt_af935adcdb63911a5d823e9b561a63aa=1594599086,1595905374; Hm_lpvt_af935adcdb63911a5d823e9b561a63aa=1595908643",
            "dnt": "1",
            "if-modified-since": "Mon, 27 Jul 2020 11:17:45 GMT",
            'if-none-match': 'W/"5f1eb7d9-11d88"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
        }
        return headers

    def __getPages(self, url):
        try:
            response = requests.get(url, timeout = 10, headers = self.__httpHeader())
            response.encoding = response.apparent_encoding
            fullDocStr = response.text
            regTxt = r'<a href="(.*?)">尾页</a>'
            reg = re.compile(regTxt, re.S)
            pageDoc = re.findall(reg, fullDocStr)
            print(pageDoc)
            return 3
        except TimeoutError as e:
            print("解析时间超时，程序退出 %s " % e)
            sys.exit(0)


    def parseCategory(self, categoryUrl, pageNum):
        totalPage = self.__getPages(categoryUrl)
        print("开始页数: %d, 总页数: %d" % (pageNum, totalPage))
        startUrl = categoryUrl
        if "http" in startUrl:
            for i in range(pageNum, totalPage):
                parseUrl = startUrl + "index_" + str(i) + ".html"
                print(parseUrl)


    # 获取数据库连接
    def get_sqlite_connect(self):
        # 数据库地址，此处为执行时的路径
        file_sqlite3_location = "db/duotoo.db"
        conn = sqlite3.connect(file_sqlite3_location)
        return conn


    def create_tables(self):
        conn = self.get_sqlite_connect()
        cursor = conn.cursor()
        create_table_script = \
            'CREATE TABLE if not exists ' \
            '"store_resource_image" ("image_id" INTEGER NOT NULL ON CONFLICT ABORT PRIMARY KEY AUTOINCREMENT,' \
            '"image_alt" TEXT(128),"image_tags" TEXT(255),"image_org_url" TEXT(255),' \
            '"image_thumb_nail_url" TEXT(255),"image_category_id" TEXT(20),"image_state" TEXT(3) );'
        cursor.execute(create_table_script)
        create_index_script = \
            'CREATE INDEX if not exists "idx_source_image_org_url" ON "store_resource_image" ("image_org_url" ASC );'
        cursor.execute(create_index_script)


    # 判断指定地址在数据库表中是否已经存在
    def exists_data_image(self, url):
        ets = False
        conn = self.get_mysql_connect()
        cursor = conn.cursor()
        sql_select = "SELECT image_id \
                    FROM store_resource_image WHERE image_org_url = '%s' limit 1" % url
        cursor.execute(sql_select)
        result = cursor.fetchone()
        if result is not None:
            ets = True
        else:
            ets = False
        conn.close()
        return ets


if __name__ == '__main__':
    duotoo = duotooImage()
    for categoryUrl in duotoo.categoryUrls:
        duotoo.parseCategory(categoryUrl, 1)
