# -*- coding:utf-8 -*- 

# ***************************************************************************
#                                  Frame.py
#                             -------------------
#    update               : 2013-11-13
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
import OpenGL
OpenGL.FORWARD_COMPATIBLE_ONLY = True
#OpenGL.ERROR_CHECKING = False
#OpenGL.ERROR_LOGGING = False
OpenGL.ERROR_ON_COPY = True
from OpenGL.GL import *
from OpenGL.GLUT import *
from math import *
from numpy import *
from Shader import *
from Transformation import *


#--
#
# Frame
#
#--
#
# Create an OpenGL frame
#
class Frame :


	#
	# Initialisation
	#
	def __init__( self, title="Untitled Window", width=1024, height=768 ) :
		# Initialise member variables
		self.title = title
		self.width  = width
		self.height = height
		self.frame_count = 0
		self.projection_matrix_id = 0
		self.view_matrix_id = 0
		self.model_matrix_id = 0
		self.shader_program_id = 0
		self.projection_matrix = identity( 4, dtype=float32 )
		self.view_matrix = identity( 4, dtype=float32 )
		self.model_matrix = identity( 4, dtype=float32 )
		self.trackball_transform = identity( 4, dtype=float32 )
		# Initialise OpenGL / GLUT
		glutInit()
		glutInitWindowSize( self.width, self.height )
		glutCreateWindow( title )
		glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH )
		# GLUT function binding
		glutCloseFunc( self.Close )
		glutDisplayFunc( self.Display )
		glutIdleFunc( self.Idle )
		glutKeyboardFunc( self.Keyboard )
		glutMouseFunc( self.Mouse )
		glutReshapeFunc( self.Reshape )
		glutTimerFunc( 0, self.Timer, 0 )
		# Color configuration
#		glClearColor( 1, 1, 1, 1 )
		glEnable( GL_DEPTH_TEST )
		glDepthFunc( GL_LESS )
		glEnable( GL_CULL_FACE )
		glCullFace( GL_BACK )
		glFrontFace( GL_CCW )
		# Initialise view matrix
		TranslateMatrix( self.view_matrix, 0, 0, -2 )
		# Create and compile GLSL program
		self.shader_program_id = LoadShaders()
		model_matrix_id = glGetUniformLocation( self.shader_program_id, "ModelMatrix" )
		view_matrix_id = glGetUniformLocation( self.shader_program_id, "ViewMatrix" )
		projection_matrix_id = glGetUniformLocation( self.shader_program_id, "ProjectionMatrix" )
		# Error checkup
		error = glGetError()
		if error != GL_NO_ERROR :
			raise RuntimeError( gluErrorString(error) )




	#
	# PrintInfo
	#
	def PrintInfo( self ) :
		print '~~~ OpenGL Informations ~~~'
		print '  Vendor :   ' + glGetString( GL_VENDOR )
		print '  Renderer : ' + glGetString( GL_RENDERER )
		print '  Version :  ' + glGetString( GL_VERSION )
		print '  Shader :   ' + glGetString( GL_SHADING_LANGUAGE_VERSION )


	#
	# Keyboard
	#
	def Keyboard( self, key, mouseX, mouseY ) :
		glutPostRedisplay()


	#
	# Mouse
	#
	def Mouse( self, button, state, x, y ) :
		if button == GLUT_LEFT_BUTTON:
			self.MouseLeftClick(x, y)
		elif button == GLUT_MIDDLE_BUTTON:
			self.MouseMiddleClick(x, y)
		elif button == GLUT_RIGHT_BUTTON:
			self.MouseRightClick(x, y)
		else:
			raise ValueError(button)
		glutPostRedisplay()


	#
	# MouseLeftClick
	#
	def MouseLeftClick( self, x, y ) :
		pass


	#
	# MouseMiddleClick
	#
	def MouseMiddleClick( self, x, y ) :
		pass


	#
	# MouseRightClick
	#
	def MouseRightClick( self, x, y ) :
		pass


	#
	# Reshape
	#
	def Reshape( self, width, height ) :
		self.width  = width
		self.height = height
		glViewport( 0, 0, self.width, self.height )
		self.projection_matrix = PerspectiveMatrix( 60, float(self.width) / float(self.height), 1.0, 100.0 )
		glUseProgram( self.shader_program_id )
		glUniformMatrix4fv( self.projection_matrix_id, 1, GL_FALSE, self.projection_matrix )
		glUseProgram( 0 )


	#
	# Display
	#
	def Display( self ) :
		# Clear all pixels and depth buffer
		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
		# Framerate counter
		self.frame_count += 1
		# Swap buffers
		glutSwapBuffers()
		glutPostRedisplay()


	#
	# Idle
	#
	def Idle( self ) :
		glutPostRedisplay()


	#
	# Close
	#
	def Close( self ) :
		# Delete shader program
		glUseProgram( 0 )
		glDeleteProgram( self.shader_program_id )
		# Error checkup
		error = glGetError()
		if error != GL_NO_ERROR :
			raise RuntimeError( gluErrorString(error) )


	#
	# TrackballMapping
	#
	def TrackballMapping( self, x, y ) :
		# Adapted from Nate Robins' programs
		# http://www.xmission.com/~nate
		v = zeros( 3 )
		v[0] = ( 2.0 * float(x) - float(self.width) ) / float(self.width)
		v[1] = ( float(self.height) - 2.0 * float(y) ) / float(self.height)
		d = norm( v )
		if d > 1.0 : d = 1.0
		v[2] = cos( pi / 2.0 * d )
		return v / norm(v)


	#
	# Timer
	#
	def Timer( self, value ) :
		if value :
			title = self.title + ' - {} FPS @ {} x {}'.format( self.frame_count * 4, self.width, self.height )
			glutSetWindowTitle( title )     
		self.frame_count = 0
		glutTimerFunc( 250, self.Timer, 1 )
	

	#
	# Run
	#
	@staticmethod
	def Run() :
		# Start up the main loop
		glutMainLoop()