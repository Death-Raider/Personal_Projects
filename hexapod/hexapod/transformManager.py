from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster, StaticTransformBroadcaster

class TransformManager:
    def __init__(self,node_cls, type:str):
        if type not in ('static', 'dynamic'):
            print("Defaulting to Static Transform Broadcast")
        self.broadcast = TransformBroadcaster(node_cls) if type == 'dynamic' else StaticTransformBroadcaster(node_cls)
        self.transform = TransformStamped()

    def set_transform(self,parent:str,child:str,transform:list[float],timestamp=None):
        if timestamp:
            self.transform.header.stamp = timestamp
        self.transform.header.frame_id = parent
        self.transform.child_frame_id = child
        self.transform.transform.translation.x = transform[0]
        self.transform.transform.translation.y = transform[1]
        self.transform.transform.translation.z = transform[2]
        self.transform.transform.rotation.x = transform[3]
        self.transform.transform.rotation.y = transform[4]
        self.transform.transform.rotation.z = transform[5]
        self.transform.transform.rotation.w = transform[6]

    def reset_transform(self):
        self.transform = TransformStamped()

    def broadcast_transform(self):
        self.broadcast.sendTransform(self.transform)
