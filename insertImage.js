conn = new Mongo()
db = conn.getDB("VoiceImageDB");
user_id = "e1a09024-af3c-4734-966c-c4b3f41dc1a2"

//Lu jia zui
var LJZname = ["IMG_1356.JPG", "IMG_1357.JPG","IMG_1358.JPG","IMG_1359.JPG","IMG_1360.JPG","IMG_1361.JPG","IMG_1362.JPG","IMG_1363.JPG","IMG_1364.JPG","IMG_1365.JPG","IMG_1366.JPG"]
var startNum = 0;
var LJZLocation = [31.237185, 121.525490]
var temp = 10;
for(i = 0; i < LJZname.length; i++) {
	if(!db.voice_images.findOne({"image_name": LJZname[i]})) {
		var dateStr = "2014-02-" + temp + "T09:05:17.171Z"
		var LJZTime = ISODate(dateStr);
		db.voice_images.save({"user_id": user_id, "image_name": LJZname[i], "time": LJZTime, "location": {"longitude": LJZLocation[0], "latitude": LJZLocation[1]}, "desc":"", "processed": true, "tags": ["lu-jia-zui","test"]});
		print("Record added as:" + LJZname[i]);
	}
	temp++;
}

//Tian an men
var TAMname = ["IMG_1338.JPG", "IMG_1339.JPG","IMG_1340.JPG","IMG_1341.JPG","IMG_1342.JPG","IMG_1343.JPG","IMG_1344.JPG","IMG_1345.JPG","IMG_1346.JPG"]
var TAMLocation = [39.908722, 116.397499]
temp = 10
for(i = 0; i < TAMname.length; i++) {
	if(!db.voice_images.findOne({"image_name": TAMname[i]})) {
		var dateStr = "2014-03-" + temp + "T09:05:17.171Z"
		var TAMTime = ISODate(dateStr);
		db.voice_images.save({"user_id": user_id, "image_name": TAMname[i], "time": TAMTime, "location": {"longitude": TAMLocation[0], "latitude": TAMLocation[1]}, "desc":"", "processed": true, "tags": ["tian-an-men","test"]});
		print("Record added as:" + TAMname[i]);
	}
	temp++;
}

//Bing ma yong
var BMYname = ["IMG_1367.JPG", "IMG_1368.JPG","IMG_1369.JPG","IMG_1370.JPG","IMG_1371.JPG","IMG_1372.JPG","IMG_1373.JPG","IMG_1374.JPG","IMG_1375.JPG","IMG_1376.JPG","IMG_1377.JPG","IMG_1378.JPG","IMG_1379.JPG"]
var BMYLocation = [34.263161, 108.948021]
temp = 10;
for(i = 0; i < BMYname.length; i++) {
	if(!db.voice_images.findOne({image_name: BMYname[i]})) {
		var dateStr = "2014-01-" + temp + "T09:05:17.171Z"
		var BMYTime = ISODate(dateStr);
		db.voice_images.save({"user_id": user_id, "image_name": BMYname[i], "time": BMYTime, "location": {"longitude": BMYLocation[0], "latitude": BMYLocation[1]}, "desc":"", "processed": true, "tags": ["bing-ma-yong","test"]});
		print("Record added as:" + BMYname[i]);
	}
	temp++;
}

//Spring festival
var SFname = ["IMG_1347.JPG", "IMG_1348.JPG","IMG_1349.JPG","IMG_1350.JPG","IMG_1351.JPG","IMG_1352.JPG","IMG_1353.JPG","IMG_1354.JPG","IMG_1355.JPG"]
var SFLocation = [30.123456, 120.789456]
temp = 10;
for(i = 0; i < SFname.length; i++) {
	if(!db.voice_images.findOne({image_name: SFname[i]})) {
		var dateStr = "2015-02-19T09:" + temp +":17.171Z"
		var SFdate = ISODate(dateStr);
		db.voice_images.save({"user_id": user_id, "image_name": SFname[i], "time": SFdate, "location": {"longitude": SFLocation[0], "latitude": SFLocation[1]}, "desc":"", "processed": true, "tags": ["chun-jie","test"]});
		print("Record added as:" + SFname[i]);
	}
	temp++;
}

//Summer
var SMname = ["IMG_1330.JPG", "IMG_1331.JPG","IMG_1332.JPG","IMG_1333.JPG","IMG_1334.JPG","IMG_1335.JPG","IMG_1336.JPG"]
var SMLocation = [38.456123, 115.456123]
temp = 10;
for(i = 0; i < SMname.length; i++) {
	if(!db.voice_images.findOne({image_name: SMname[i]})) {
		var dateStr = "2014-06-" + temp + "T09:05:17.171Z"
		var SMdate = ISODate(dateStr);
		db.voice_images.save({"user_id": user_id, "image_name": SMname[i], "time": SMdate, "location": {"longitude": SMLocation[0], "latitude": SMLocation[1]}, "desc":"", "processed": true, "tags": ["xia-tian","test"]});
		print("Record added as:" + SMname[i]);
	}
	temp++;
}