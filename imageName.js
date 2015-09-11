conn = new Mongo()
db = conn.getDB("VoiceImageDB");

var ex = "IMG_"
var suffix = ".JPG"
var user_id = "b42c916c-3b1e-4235-85b7-451aea401218"   //need modified

function imageName(startNum, length) {
	result = []
	for(i = 0; i < LJZlength; i++){
		var num = startNum + i;
		var s = "000" + num;
		var item = ex + s.substr(s.length-4, s.length-1) + suffix;
		result.push(item);
    }
    return result;
}

//Lu jia zui
var LJZbegin = 1   //need modified
var LJZlength = 10   //need modified
var LJZname = imageName(LJZbegin, LJZlength);
var LJZLocation = [31.237185, 121.525490]
var temp = 10
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
var TAMbegin = 1   //need modified
var TAMlength = 10   //need modified
var TAMname = imageName(TAMbegin, TAMlength);
temp = 10;
var TAMLocation = [39.908722, 116.397499]
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
var BMYbegin = 50   //need modified
var BMYlength = 10  //need modified
var BMYname = imageName(BMYbegin, BMYlength)
temp = 10
var BMYLocation = [34.263161, 108.948021]
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
var SFbegin = 100   //need modified
var SFlength = 10   //need modified
var SFname = imageName(SFbegin, SFlength)
temp = 10;
var SFLocation = [30.123456, 120.789456]
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
var SMbegin = 111   //need modified
var SMlength = 10   //need modified
var SMname = imageName(SMbegin, SMlength)
temp = 10;
var SMLocation = [38.456123, 115.456123]
for(i = 0; i < SMname.length; i++) {
	if(!db.voice_images.findOne({image_name: SMname[i]})) {
		var dateStr = "2014-06-" + temp + "T09:05:17.171Z"
		var SMdate = ISODate(dateStr);
		db.voice_images.save({"user_id": user_id, "image_name": SMname[i], "time": SMdate, "location": {"longitude": SMLocation[0], "latitude": SMLocation[1]}, "desc":"", "processed": true, "tags": ["xia-tian","test"]});
		print("Record added as:" + SMname[i]);
	}
	temp++;
}
