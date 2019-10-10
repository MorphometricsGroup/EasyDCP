import Metashape
doc = Metashape.app.document
chunk = doc.chunk
for camera in chunk.cameras:
   yaw = 0#float(camera.photo.meta["DJI/GimbalYawDegree"])
   pitch = 0#float(camera.photo.meta["DJI/GimbalPitchDegree"])
   roll = 0#float(camera.photo.meta["DJI/GimbalRollDegree"])
   camera.reference.rotation = Metashape.Vector([yaw, pitch, roll])