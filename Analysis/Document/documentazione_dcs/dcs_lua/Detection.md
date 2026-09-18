#### Detection

```
 Controller.Detection = {
   VISUAL,
   OPTIC,
   RADAR,
   IRST,
   RWR,
   DLINK
 }

```

enum contains identifiers of surface types.

```
 function 
     boolean detected,
     boolean visible,
     ModelTime lastTime,
     boolean type,
     boolean distance,
     Vec3 lastPos,
     Vec3 lastVel,
                     Controller.isTargetDetected(Controller self,
                                                 Object target,
                                                 [Controller.Detection detection1,
                                                  Controller.Detection detection2,
                                                  ...
                                                  Controller.Detection detectionN] or nil) 

```

checks if the target is detected or not. If one or more detection method is specified the function will return true if the target is detected by at least one of these methods. If no detection methods are specified the function will return true if the target is detected by any method.

_target_

-   Target to check.

_detection1_ - _detectionN_

-   Detection methods of interest.

Return values:

_detected_

-   True if the target is detected.

_visible_

-   Has effect only if _detected_ is true. True if the target is visible now.

_type_

-   Has effect only if _detected_ is true. True if the target type is known.

_distance_

-   Has effect only if _detected_ is true. True if the distance to the target is known.

_lastTime_

-   Has effect only if _visible_ is false. Last time when target was seen.

_lastPos_

-   Has effect only if _visible_ is false. Last position of the target when it was seen.

_lastVel_

-   Has effect only if _visible_ is false. Last velocity of the target when it was seen.

```
 DetectedTarget = {
   object = Object, --the target
   visible = boolean, --the target is visible
   type = boolean, --the target type is known
   distance = boolean --distance to the target is known
 }

```

detected target.

```
 DetectedTargets = array of DetectedTarget

```

list of detected targets.

```
 function array DetectedTargets Controller.getDetectedTargets(Controller self,
                                                              [Controller.Detection detection1,
                                                               Controller.Detection detection2,
                                                                 ...
                                                               Controller.Detection detectionN] or nil)

```

returns list of detected targets. If one or more detection method is specified the function will return targets which were detected by at least one of these methods. If no detection methods are specified the function will return targets which were detected by any method.

_detection1_ - _detectionN_

-   Detection methods of interest.

```
 function Controller.knowTarget(Controller self, Object object, boolean type, boolean distance)

```

_object_

-   The target.

_type_

-   Target type is known.

_distance_

-   Distance to the target type is known.