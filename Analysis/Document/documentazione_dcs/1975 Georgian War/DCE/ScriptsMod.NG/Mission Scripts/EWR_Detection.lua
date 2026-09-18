


AWACS_USA_Unit = Unit.getByName('EWR01')

if AWACS_USA_Unit ~= nil then
    AWACS_USA_Ctrl = AWACS_USA_Unit:getGroup():getController()
    local Targets = AWACS_USA_Ctrl:getDetectedTargets(VISUAL, RADAR, RWR)

    if #Targets > 0 then
        local InterestingTargets = 0

        for n = 1, #Targets do

            if Targets[n].object:isExist() == true and Targets[n].object:inAir() == true and Targets[n].object:getCoalition() == 2 then
                InterestingTargets = InterestingTargets + 1
                local TargetPosition = Targets[n].object:getPosition()
                local ZoneInfo = trigger.misc.getZone('detection01')
                local DistanceToZone = math.sqrt(math.pow(TargetPosition.p.x - ZoneInfo.point.x, 2) + math.pow(TargetPosition.p.z - ZoneInfo.point.z, 2))
                env.info("DistanceToZone "..DistanceToZone.. " <= ZoneInfo.radius "..ZoneInfo.radius.." TGTx: "..TargetPosition.p.x.." TGTy: "..TargetPosition.p.y.." TGTz: "..TargetPosition.p.z)
                env.info(" Zonex: "..ZoneInfo.point.x.." Zoney: "..ZoneInfo.point.y.." ZoneZ: "..ZoneInfo.point.z)

				if DistanceToZone <= ZoneInfo.radius then
                    return true
                end
            end
        end
    end
end