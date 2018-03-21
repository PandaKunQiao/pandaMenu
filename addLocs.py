import maya.cmds as cmds
TWISTPRE = "twist_"
TWISTSUR = "_start"
NORMPRE = "mult_key_"

def createDriverLocs():
	jntList = cmds.ls(selection = True, flatten = True)
	for jnt in jntList:
		locVarName = jnt[3:]
		midPosition = cmds.xform(jnt, query = True, 
								worldSpace = True, matrix = True)
		locPrefix = "loc_driver_" + locVarName + "_"

		# to create all required locators
		locMid = cmds.spaceLocator(name = locPrefix + "midStart")[0]
		locFbStay = cmds.spaceLocator(name = locPrefix + "fbEnd_stay")[0]
		locFbMove = cmds.spaceLocator(name = locPrefix + "fbEnd_move")[0]
		refFbMove = cmds.createNode("transform", name = "ref_" + locFbMove)

		locUdStay = cmds.spaceLocator(name = locPrefix + "udEnd_stay")[0]
		locUdMove = cmds.spaceLocator(name = locPrefix + "udEnd_move")[0]
		refUdMove = cmds.createNode("transform", name = "ref_" + locUdMove)

		locLs = [locMid, 
				 locFbStay, locFbMove, locUdStay, locUdMove, 
				 refFbMove, refUdMove]

		# put all of them to the joint position
		for eachNode in locLs:
			cmds.xform(eachNode, matrix = midPosition, worldSpace = True)

		# zero out move locs
		cmds.parent(locFbMove, refFbMove)
		cmds.parent(locUdMove, refUdMove)

		# put them forward
		cmds.setAttr(locFbMove + ".translateZ", 1.0)
		cmds.setAttr(locUdMove + ".translateY", 1.0)
		fbPos = cmds.xform(locFbMove, query = True,
							worldSpace = True, matrix = True)
		udPos = cmds.xform(locUdMove, query = True, 
							worldSpace = True, matrix = True)
		cmds.xform(refFbMove, worldSpace = True, matrix = fbPos)
		cmds.xform(refUdMove, worldSpace = True, matrix = udPos)
		cmds.xform(locFbStay, worldSpace = True, matrix = fbPos)
		cmds.xform(locUdStay, worldSpace = True, matrix = udPos)

		cmds.setAttr(locFbMove + ".translateX", 0.0)
		cmds.setAttr(locFbMove + ".translateY", 0.0)
		cmds.setAttr(locFbMove + ".translateZ", 0.0)
		cmds.setAttr(locUdMove + ".translateX", 0.0)
		cmds.setAttr(locUdMove + ".translateY", 0.0)
		cmds.setAttr(locUdMove + ".translateZ", 0.0)

		groupNode = cmds.createNode("transform", 
									name = "grp_driver_" + locPrefix[:-1])
		cmds.parent([locMid, locFbStay, refFbMove, locUdStay, refUdMove], 
					groupNode)

		# add constraint to those locators
		twistDriver = TWISTPRE + locVarName + TWISTSUR
		if (("_shoulder_" in jnt) or ("_femur_" in jnt)):
			cmds.pointConstraint(jnt, locMid, maintainOffset = True)
			cmds.pointConstraint(jnt, locUdStay, maintainOffset = True)
			cmds.pointConstraint(jnt, locFbStay, maintainOffset = True)
			cmds.pointConstraint(locUdStay, refUdMove, maintainOffset = True)
			cmds.pointConstraint(locFbStay, refFbMove, maintainOffset = True)
		cmds.parentConstraint(twistDriver, locUdMove, maintainOffset = True)
		cmds.parentConstraint(twistDriver, locFbMove, maintainOffset = True)

		# set up NON-DAG nodes

		# create decompose matrix node for each loc
		matrixMid = cmds.createNode("decomposeMatrix", name = "matrix_" + locVarName + "_midStart")
		matrixFbStay = cmds.createNode("decomposeMatrix", name = "matrix_" + locVarName + "_fbEnd_stay")
		matrixFbMove = cmds.createNode("decomposeMatrix", name = "matrix_" + locVarName + "_fbEnd_move")
		matrixUdStay = cmds.createNode("decomposeMatrix", name = "matrix_" + locVarName + "_udEnd_stay")
		matrixUdMove = cmds.createNode("decomposeMatrix", name = "matrix_" + locVarName + "_udEnd_move")

		# connect world matrix to each decompose matrix
		cmds.connectAttr(locMid + ".worldMatrix[0]", matrixMid + ".inputMatrix")
		cmds.connectAttr(locFbStay + ".worldMatrix[0]", matrixFbStay + ".inputMatrix")
		cmds.connectAttr(locFbMove + ".worldMatrix[0]", matrixFbMove + ".inputMatrix")
		cmds.connectAttr(locUdStay + ".worldMatrix[0]", matrixUdStay + ".inputMatrix")
		cmds.connectAttr(locUdMove + ".worldMatrix[0]", matrixUdMove + ".inputMatrix")

		# create vectors for angles
		vecUdMove = cmds.createNode("plusMinusAverage", name = "vec_" + locVarName + "_ud_move")
		vecUdStay = cmds.createNode("plusMinusAverage", name = "vec_" + locVarName + "_ud_stay")
		vecFbMove = cmds.createNode("plusMinusAverage", name = "vec_" + locVarName + "_fb_move")
		vecFbStay = cmds.createNode("plusMinusAverage", name = "vec_" + locVarName + "_fb_stay")
		cmds.setAttr(vecUdMove + ".operation", 2)
		cmds.setAttr(vecUdStay + ".operation", 2)
		cmds.setAttr(vecFbMove + ".operation", 2)
		cmds.setAttr(vecFbStay + ".operation", 2)
		cmds.connectAttr(matrixUdMove + ".outputTranslate", vecUdMove + ".input3D[1]")
		cmds.connectAttr(matrixUdStay + ".outputTranslate", vecUdStay + ".input3D[1]")
		cmds.connectAttr(matrixFbMove + ".outputTranslate", vecFbMove + ".input3D[1]")
		cmds.connectAttr(matrixFbStay + ".outputTranslate", vecFbStay + ".input3D[1]")
		cmds.connectAttr(matrixMid + ".outputTranslate", vecUdMove + ".input3D[0]")
		cmds.connectAttr(matrixMid + ".outputTranslate", vecUdStay + ".input3D[0]")
		cmds.connectAttr(matrixMid + ".outputTranslate", vecFbMove + ".input3D[0]")
		cmds.connectAttr(matrixMid + ".outputTranslate", vecFbStay + ".input3D[0]")

		# create angles
		angleUd = cmds.createNode("angleBetween", name = "angle_" + locVarName + "_ud")
		angleFb = cmds.createNode("angleBetween", name = "angle_" + locVarName + "_fb")
		cmds.connectAttr(vecUdMove + ".output3D", angleUd + ".vector1")
		cmds.connectAttr(vecUdStay + ".output3D", angleUd + ".vector2")
		cmds.connectAttr(vecFbMove + ".output3D", angleFb + ".vector1")
		cmds.connectAttr(vecFbStay + ".output3D", angleFb + ".vector2")

		# create nodition nodes
		condUd = cmds.createNode("condition", name = "cond_" + locVarName + "_ud")
		condFb = cmds.createNode("condition", name = "cond_" + locVarName + "_fb")
		cmds.setAttr(condUd + ".operation", 2)
		cmds.setAttr(condFb + ".operation", 2)
		cmds.setAttr(condUd + ".colorIfTrueG", -1)
		cmds.setAttr(condFb + ".colorIfTrueG", -1)
		cmds.connectAttr(locUdMove + ".translateX", condUd + ".firstTerm")
		cmds.connectAttr(locFbMove + ".translateX", condFb + ".firstTerm")

		# create normalizers
		multNormY = NORMPRE + locVarName + "_y"
		multNormZ = NORMPRE + locVarName + "_z"
		if cmds.objExists(multNormY) == False:
			cmds.createNode("multiplyDivide", name = multNormY)
		if cmds.objExists(multNormZ) == False:
			cmds.createNode("multiplyDivide", name = multNormZ)
		cmds.connectAttr(angleUd + ".eulerZ", multNormZ + ".input1Z", force = True)
		cmds.connectAttr(angleFb + ".eulerY", multNormY + ".input1Y", force = True)
		cmds.connectAttr(condUd + ".outColorG", multNormZ + ".input2Z", force = True)
		cmds.connectAttr(condFb + ".outColorG", multNormY + ".input2Y", force = True)
		

	return groupNode

createDriverLocs()
