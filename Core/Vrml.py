# -*- coding:utf-8 -*- 

# ***************************************************************************
#                                  Vrml.py
#                             -------------------
#    update               : 2013-11-12
#    copyright            : (C) 2013 by Michaël Roy
#    email                : microygh@gmail.com
# ***************************************************************************

# ***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************


#
# External dependencies
#
from Mesh import *
from numpy import *


#--
#
# ReadVrmlFile
#
#--
#
# Import mesh from a file in Inventor / VRML / X3D format
#
def ReadVrmlFile( filename ) :
	# Initialisation
	vertices = []
	faces = []
	normals = []
	colors = []
	texcoords = []
        material = ''
	nlbrack = 0
	nrbrack = 0
	level = 0
	ixyz = 0
	nodes = ['']
	vec2d = [0., 0.]
	vec3d = [0., 0., 0.]
	vec3i = [0, 0, 0]
	previous_word = ''
	color_binding=""
	normal_binding=""
	# Open the file
	vrmlfile = open( filename, 'r' )
	# Check the header
	header = vrmlfile.readline().split()
	if header[0] not in [ '#VRML', '#X3D', '#Inventor' ] :
		vrmlfile.close()
		raise StandardError( 'Wrong file format !' )
	# Read each line in the file
	for line in vrmlfile :
		# Empty line
		if line.isspace() : continue
		# Comment
		if line.startswith( '#' ) : continue
		# Remove comma
		line = line.replace( ',', ' ' )
		# Add buffer space around brackets and braces
		line = line.replace( '[', ' [ ' ).replace( '{', ' { ' ).replace( ']', ' ] ' ).replace( '}', ' } ' )
		# Split values in the line
		for word in line.split() :
			# Left bracket or brace
			if word in [ '[', '{' ] :
				# Increment left deliminter number
				nlbrack += 1
				# Get level number
				level = nlbrack - nrbrack
				# Save level name
				if level >= len(nodes) : nodes.append( previous_word )
				else : nodes[level] = previous_word
				# Initialize coordinate index
				ixyz = 0
			# Right bracket or brace
			elif word in [ '}', ']' ] :
				# Increment right deliminter number
				nrbrack += 1
				# Get level number
				level = nlbrack - nrbrack
				# Sanity check
				if level < 0 : return None
			# Comment
			elif word.startswith('#') :
				# Save current word
				previous_word = word
				# Next line
				break
			# Point
			elif nodes[level] == 'point' :
				# Geometry
				if nodes[level-1] in [ 'Coordinate', 'Coordinate3' ] :
					# Get current value
					vec3d[ixyz] = float( word )
					# Complete coordinate ?
					if ixyz == 2 :
						vertices.append( vec3d[:] )
						ixyz = 0
					else :
						ixyz += 1
				# Texture
				elif nodes[level-1] in [ 'TextureCoordinate', 'TextureCoordinate2' ] :
					# Get current value
					vec2d[ixyz] = float( word )
					# Complete coordinate ?
					if ixyz == 1 :
						texcoords.append( vec2d[:] ) 
						ixyz = 0
					else :
						ixyz += 1
			# Face
			elif nodes[level] == 'coordIndex' :
				# Color binding
				if previous_word == 'colorPerVertex' and word == 'TRUE' :
					color_binding = 'PER_VERTEX'
					continue
				# Normal binding
				elif previous_word == 'normalPerVertex' and word == 'TRUE' :
					normal_binding = 'PER_VERTEX'
					continue
				# Face indices
				elif nodes[level-1] == 'IndexedFaceSet' :
					# -1 value
					if ixyz == 3 :
						# Next face
						ixyz = 0
						continue
					# Get value
					vec3i[ixyz] = int( word )
					# Complete coordinate ?
					if ixyz == 2 :
						faces.append( vec3i[:] )
					# Next coordinate
					ixyz += 1
			# Color (VRML 2)
			elif nodes[level] == 'color' :
				if nodes[level-1] == 'Color' :
					# Get current value
					vec3d[ixyz] = float( word )
					# Complete coordinate ?
					if ixyz == 2 :
						colors.append( vec3d[:] )
						ixyz = 0
					else :
						# Next coordinate
						ixyz += 1
			# Color (VRML 1)
			elif nodes[level] == 'diffuseColor' :
				if nodes[level-1] == 'Material' :
					# Get current value
					vec3d[ixyz] = float( word )
					# Complete coordinate ?
					if ixyz == 2 :
						colors.append( vec3d[:] )
						ixyz = 0
					else :
						# Next coordinate
						ixyz += 1
			# Normal
			elif nodes[level] == 'vector' :
				if nodes[level-1] == 'Normal' :
					# Get current value
					vec3d[ixyz] = float( word )
					# Complete coordinate ?
					if ixyz == 2 :
						normals.append( vec3d[:] )
						ixyz = 0
					else :
						# Next coordinate
						ixyz += 1
			# Texture filename
			elif nodes[level] == 'ImageTexture' :
				if previous_word == 'url' :
					if len(word) > 2 :
						# Get texture filename
						# Remove quotes around the filename
						material = word[ 1 : -1 ]
			# Texture filename
			elif nodes[level] == 'Texture2' :
				if previous_word == 'filename' :
					if len(word) > 2 :
						# Get texture filename
						# Remove quotes around the filename
						material = word[ 1 : -1 ]
			# Color binding
			elif nodes[level] == 'MaterialBinding' :
				if previous_word == 'value' :
					color_binding = word
			# Normal binding
			elif nodes[level] == 'NormalBinding' :
				if previous_word == 'value' :
					normal_binding = word
			
			# Save current word
			previous_word = word

	# Close the file
	vrmlfile.close()

	# Only accept per vertex binding
#	if material_binding is not 'PER_VERTEX' : colors=[]
#	if normal_binding is not 'PER_VERTEX' : normals=[]

	#
	# TODO: Check mesh
	#

	# Return the final mesh
	return Mesh( name=filename, vertices=array(vertices, dtype=float32), faces=array(faces, dtype=uint32),
		vertex_normals=array(normals, dtype=float32), colors=array(colors, dtype=float32),
		textures=array(texcoords, dtype=float32), texture_name=material )


#--
#
# WriteVrmlFile
#
#--
#
# Export mesh to a VRML V2.0 file
#
def WriteVrmlFile( mesh, filename ) :

	# Open the file
	vrmlfile = open( filename, 'w' )

	#
	# TODO: Check mesh/file
	# 


	# Write file Header
	vrmlfile.write( '#VRML V2.0 utf8\n\n' );

	# Write vertex number (comment)
	vrmlfile.write( '# Vertices:  {}\n'.format(len(mesh.vertices)) )
	# Write face number (comment)
	vrmlfile.write( '# Faces:     {}\n\n'.format(len(mesh.faces)) )

	# Begin description
	vrmlfile.write( 'Transform {\n' )
	vrmlfile.write( '  scale 1 1 1\n' )
	vrmlfile.write( '  translation 0 0 0\n' )
	vrmlfile.write( '  children [\n' )
	vrmlfile.write( '    Shape {\n' )

	# Texture filename
	if ( len(mesh.textures) == len(mesh.vertices) ) and ( mesh.texture_name is not '' ) :
		vrmlfile.write( '      appearance Appearance {\n' )
		vrmlfile.write( '        texture ImageTexture {\n' )
		vrmlfile.write( '          url "{}"\n'.format(mesh.texture_name) )
		vrmlfile.write( '        }\n' )
		vrmlfile.write( '      }\n' )

	# Vertex coordinates
	vrmlfile.write( '      geometry IndexedFaceSet {\n' )
	vrmlfile.write( '        coord Coordinate {\n' )
	vrmlfile.write( '          point [\n' )
	for i in range( len(mesh.vertices)-1 ) :
		vrmlfile.write( '                {0} {1} {2},\n'.format( mesh.vertices[i,0], mesh.vertices[i,1], mesh.vertices[i,2] ) )
	vrmlfile.write( '                {0} {1} {2}\n'.format( mesh.vertices[len(mesh.vertices)-1,0], mesh.vertices[len(mesh.vertices)-1,1], mesh.vertices[len(mesh.vertices)-1,2] ) )
	vrmlfile.write( '          ]\n' )
	vrmlfile.write( '        }\n' )

	# Face indices
	vrmlfile.write( '        coordIndex [\n' )
	for i in range( len(mesh.faces)-1 ) :
		vrmlfile.write( '            {0}, {1}, {2}, -1,\n'.format( mesh.faces[i,0], mesh.faces[i,1], mesh.faces[i,2] ) )
	vrmlfile.write( '            {0}, {1}, {2}, -1\n'.format( mesh.faces[len(mesh.faces)-1,0], mesh.faces[len(mesh.faces)-1,1], mesh.faces[len(mesh.faces)-1,2] ) )
	vrmlfile.write( '        ]\n' )

	# Colors
	if len(mesh.colors) == len(mesh.vertices) :
		vrmlfile.write( '        colorPerVertex TRUE\n' )
		vrmlfile.write( '        color Color {\n' )
		vrmlfile.write( '          color [\n' )
		for i in range( len(mesh.colors)-1 ) :
			vrmlfile.write( '            {0} {1} {2},\n'.format( mesh.colors[i,0], mesh.colors[i,1], mesh.colors[i,2] ) )
		vrmlfile.write( '            {0} {1} {2}\n'.format( mesh.colors[len(mesh.colors)-1,0], mesh.colors[len(mesh.colors)-1,1], mesh.colors[len(mesh.colors)-1,2] ) )
		vrmlfile.write( '          ]\n' )
		vrmlfile.write( '        }\n' )

	# Vertex normals
#	if len(mesh.vertex_normals) == len(mesh.vertices) :
#		vrmlfile.write( '        normalPerVertex TRUE\n' )
#		vrmlfile.write( '        normal Normal {\n' )
#		vrmlfile.write( '          vector [\n' )
#		for i in range( len(mesh.vertex_normals)-1 ) :
#			vrmlfile.write( '            {0} {1} {2},\n'.format( mesh.vertex_normals[i,0], mesh.vertex_normals[i,1], mesh.vertex_normals[i,2] ) )
#		vrmlfile.write( '            {0} {1} {2}\n'.format( mesh.vertex_normals[len(mesh.vertex_normals)-1,0], mesh.vertex_normals[len(mesh.vertex_normals)-1,1], mesh.vertex_normals[len(mesh.vertex_normals)-1,2] ) )
#		vrmlfile.write( '          ]\n' )
#		vrmlfile.write( '        }\n' )

	# Texture coordinates
	if ( len(mesh.textures) == len(mesh.vertices) ) and ( mesh.texture_name is not '' ) :
		vrmlfile.write( '        texCoord TextureCoordinate {\n' )
		vrmlfile.write( '          point [\n' )
		for i in range( len(mesh.textures)-1 ) :
			vrmlfile.write( '            {0} {1},\n'.format( mesh.textures[i,0], mesh.textures[i,1] ) )
		vrmlfile.write( '            {0} {1}\n'.format( mesh.textures[len(mesh.textures)-1,0], mesh.textures[len(mesh.textures)-1,1] ) )
		vrmlfile.write( '          ]\n' )
		vrmlfile.write( '        }\n' )

	# End description
	vrmlfile.write( '      }\n' )
	vrmlfile.write( '    }\n' )
	vrmlfile.write( '  ]\n' )
	vrmlfile.write( '}\n' )

	# Close the file
	vrmlfile.close()

	return True

