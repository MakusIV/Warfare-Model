#### Weapon

Represents a weapon unit: shell, rocket, missile and bomb. Extends _CoalitionObject_. Final class.

**Types**

_Weapon.flag_ enum stores weapon flags. Some of them are combination of another flags.

```
 Weapon.flag = {
   LGB, 
   TvGB, 
   SNSGB, 
   
   HEBomb, 
   Penetrator, 
   NapalmBomb, 
   FAEBomb, 
   ClusterBomb, 
   Dispencer, 
   CandleBomb, 
   ParachuteBomb, 
   
   GuidedBomb = LGB + TvGB + SNSGB, 
   AnyUnguidedBomb = HEBomb + Penetrator + NapalmBomb + FAEBomb + ClusterBomb + Dispencer + CandleBomb + ParachuteBomb, 
   AnyBomb = GuidedBomb + AnyUnguidedBomb, 
   
   LightRocket, 
   MarkerRocket, 
   CandleRocket, 
   HeavyRocket, 
   
   AnyRocket = LightRocket + HeavyRocket + MarkerRocket + CandleRocket, 
   
   AntiRadarMissile, 
   AntiShipMissile, 
   AntiTankMissile, 
   FireAndForgetASM, 
   LaserASM, 
   TeleASM, 
   CruiseMissile, 
   
   GuidedASM = LaserASM + TeleASM, 
   TacticASM = GuidedASM + FireAndForgetASM, 
   AnyASM = AntiRadarMissile + AntiShipMissile + AntiTankMissile + FireAndForgetASM + GuidedASM + CruiseMissile, 
   
   SRAAM, 
   MRAAM, 
   LRAAM, 
   
   IR_AAM, 
   SAR_AAM, 
   AR_AAM, 
   
   AnyAAM = IR_AAM + SAR_AAM + AR_AAM + SRAAM + MRAAM + LRAAM, 
   
   AnyMissile = AnyASM + AnyAAM,   
   AnyAutonomousMissile = IR_AAM + AntiRadarMissile + AntiShipMissile + FireAndForgetASM + CruiseMissile,
   
   GUN_POD, 
   BuiltInCannon, 
   
   Cannons = GUN_POD + BuiltInCannon, 
   
   AnyAGWeapon = BuiltInCannon + GUN_POD + AnyBomb + AnyRocket + AnyASM, 
   AnyAAWeapon = BuiltInCannon + GUN_POD + AnyAAM, 
   
   UnguidedWeapon = Cannons + BuiltInCannon + GUN_POD + AnyUnguidedBomb + AnyRocket, 
   GuidedWeapon = GuidedBomb + AnyASM + AnyAAM, 
   
   AnyWeapon = AnyBomb + AnyRocket + AnyMissile + Cannons, 
   
   MarkerWeapon = MarkerRocket + CandleRocket + CandleBomb, 
   ArmWeapon = AnyWeapon - MarkerWeapon
 }

```

_Weapon.Category_ enum that stores weapon categories.

```
 Weapon.Category = {
   SHELL,
   MISSILE,
   ROCKET,
   BOMB
 }

```

_Weapon.GuidanceType_ enum that stores guidance methods. Available only for guided weapon (_Weapon.Category.MISSILE_ and some _Weapon.Category.BOMB_).

```
 Weapon.GuidanceType = {
   INS,
   IR,
   RADAR_ACTIVE,
   RADAR_SEMI_ACTIVE,
   RADAR_PASSIVE,
   TV,
   LASER,
   TELE
 }

```

_Weapon.MissileCategory_ enum that stores missile category. Available only for missiles (_Weapon.Category.MISSILE_).

```
 Weapon.MissileCategory = {
   AAM,
   SAM,
   BM,
   ANTI_SHIP,
   CRUISE,
   OTHER
 }

```

_Weapon.WarheadType_ enum that stores warhead types.

```
 Weapon.WarheadType = {
   AP,
   HE,
   SHAPED_EXPLOSIVE
 }

```

**Structures**

```
 Weapon.Desc = extends Object.Desc {
   category = enum Weapon.Category,
   warhead = {
     type = enum Weapon.WarheadType,
     mass = Mass,
     caliber = Distance,
     explosiveMass = Mass or nil, --for HE and AP(+HE) warheads only
     shapedExplosiveMass = Mass or nil, --for shaped explosive warheads only
     shapedExplosiveArmorThickness = Distance or nil ----for shaped explosive warheads only
   }
 }

```

weapon descriptor. This is common part of descriptor for any weapon. Some fields are actual only for HE and AP+HE warheads, some fields are actual only for shaped explosive warheads. Descriptor format depended on weapon category.

```
 Weapon.DescMissile = extends Weapon.Desc {    
   guidance = enum Weapon.GuidanceType,
   rangeMin = Distance,
   rangeMaxAltMin = Distance,
   rangeMaxAltMax = Distance,
   altMin = Distance,
   altMax = Distance,
   Nmax = number,
   fuseDist = Distance
 }

```

missile descriptor.

```
 Weapon.DescRocket = extends Weapon.Desc {
   distMin = Distance,
   distMax = Distance
 }

```

rocket descriptor.

```
 Weapon.DescBomb = extends Weapon.Desc {    
   guidance = enum Weapon.GuidanceType,
   altMin = Distance,
   altMax = Distance,
 }

```

bomb descriptor.

**Member functions**

```
 Unit Weapon.getLauncher(Weapon self)

```

returns the unit that launched the weapon

```
 Object Weapon.getTarget(Weapon self)

```

returns target of the guided weapon. Unguided weapons and guided weapon that is targeted at the point on the ground will return nil.

```
 Weapon.Desc Weapon.getDesc(Weapon self)

```

returns weapon descriptor. Descriptor type depends on weapon category.