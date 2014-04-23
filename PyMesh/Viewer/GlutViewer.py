#! /usr/bin/env python
# -*- coding:utf-8 -*- 


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
from numpy import *
from .MeshViewer import *
import sys


#
# Create an OpenGL frame with GLUT
#
class GlutViewer :


	#
	# Initialisation
	#
	def __init__( self, mesh=None, title="Untitled Window", width=1024, height=768 ) :

		# Initialise member variables
		self.title = title
		self.width  = width
		self.height = height
		self.frame_count = 0
		self.previous_mouse_position = array([0, 0])
		self.trackball = Trackball( width, height )
		self.motion_state = 0

		# Initialise OpenGL / GLUT
		glutInit()
		glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH )
		glutInitWindowSize( width, height )
		glutInitWindowPosition( 100, 100 )
		glutCreateWindow( title )

		# GLUT function binding
		glutCloseFunc( self.Close )
		glutDisplayFunc( self.Display )
		glutIdleFunc( self.Idle )
		glutKeyboardFunc( self.Keyboard )
		glutMouseFunc( self.Mouse )
		glutMotionFunc( self.Motion )
		glutReshapeFunc( self.Reshape )
		glutTimerFunc( 0, self.Timer, 0 )

		# OpenGL configuration
		glClearColor( 1, 1, 1, 1 )
		glEnable( GL_DEPTH_TEST )
		glDepthFunc( GL_LESS )
		glEnable( GL_CULL_FACE )

		# Mesh viewer initialisation
		self.mesh_viewer = MeshViewer( mesh, width, height )


	#
	# Keyboard
	#
	def Keyboard( self, key, mouseX, mouseY ) :

		# Escape
		if key == '\x1b' :

			# Exit
			sys.exit()

		# R
		elif key in [ 'r', 'R' ] :

			# Reset model translation and rotation
			self.mesh_viewer.trackball_transform = identity( 4, dtype=float32 )
			self.mesh_viewer.model_translation = array( [0, 0, 0], dtype=float32 )
			self.axes_viewer.trackball_transform = identity( 4, dtype=float32 )



	#
	# Mouse
	#
	def Mouse( self, button, state, x, y ) :

		# Button down
		if state == GLUT_DOWN :

			# Left button
			if button == GLUT_LEFT_BUTTON :

				# Trackball rotation
				self.motion_state = 1
				self.trackball.Update( x, y )

			# Middle button
			elif button == GLUT_MIDDLE_BUTTON :

				# XY translation
				self.motion_state = 2
				self.previous_mouse_position = array([ x, y ])

			# Right button
			elif button == GLUT_RIGHT_BUTTON :

				# Z translation
				self.motion_state = 3
				self.previous_mouse_position = array([ x, y ])
		
		# Button up
		elif state == GLUT_UP :

			# Stop motion
			self.motion_state = 0


	#
	# Motion
	#
	def Motion( self, x, y ) :

		# Trackball rotation
                if self.motion_state == 1 :

                        (rotation_angle, rotation_axis) = self.trackball.GetRotation( x, y )
			self.mesh_viewer.trackball_transform = RotateMatrix( self.mesh_viewer.trackball_transform,
				rotation_angle, rotation_axis )
			self.axes_viewer.trackball_transform = self.mesh_viewer.trackball_transform

		# XY translation
                elif self.motion_state ==  2 :

                        self.mesh_viewer.model_translation[0] -= float(self.previous_mouse_position[0]-x)*0.001
                        self.mesh_viewer.model_translation[1] += float(self.previous_mouse_position[1]-y)*0.001
                        self.previous_mouse_position = array([ x, y ])

		# Z translation
                elif self.motion_state ==  3 :

                        self.mesh_viewer.model_translation[2] -= float(self.previous_mouse_position[1]-y) * 0.001
                        self.previous_mouse_position = array([ x, y ])

	#
	# Reshape
	#
	def Reshape( self, width, height ) :

		# Resize the viewport
		self.width  = width
		self.height = height
		glViewport( 0, 0, width, height )

		# Recompute the perspective matrix
		self.mesh_viewer.SetPerspectiveMatrix( width, height )

		# Update the trackball
		self.trackball.Resize( width, height )


	#
	# Display
	#
	def Display( self ) :

		# Framerate counter
		self.frame_count += 1

		# Clear all pixels and depth buffer
		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

		# Display the mesh
		self.mesh_viewer.Display()

		# Resize the viewport
		glViewport( 0, 0, 100, 100 )

		# Display the XYZ axes
		self.axes_viewer.Display()

		# Restore the viewport
		glViewport( 0, 0, self.width, self.height )

		# Swap buffers
		glutSwapBuffers()
		glutPostRedisplay()

	#
	# Idle
	#
	def Idle( self ) :

		# Redraw
		glutPostRedisplay()


	#
	# Close
	#
	def Close( self ) :

		# Close the mesh
		self.mesh_viewer.Close()

		# Initialise member variables
		self.frame_count = 0
		self.previous_mouse_position = array([0, 0])
		self.previous_trackball_position = array([0.0, 0.0, 0.0 ])
		self.motion_state = 0


	#
	# Timer
	#
	def Timer( self, value ) :

		# Framerate counter
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


	#
	# PrintInfo
	#
	def PrintInfo( self ) :

		# Display OpenGL driver informations
		print( '~~~ OpenGL Informations ~~~' )
		print( '  Vendor :   ' + glGetString( GL_VENDOR ) )
		print( '  Renderer : ' + glGetString( GL_RENDERER ) )
		print( '  Version :  ' + glGetString( GL_VERSION ) )
		print( '  Shader :   ' + glGetString( GL_SHADING_LANGUAGE_VERSION ) )


#
# Main
#
if __name__ == "__main__":
  
	m = ReadVrmlFile( "bunny.wrl" )
	UpdateNormals( m )
	print m
	CheckMesh( m )
	v = GlutViewer( mesh=m, title="Test" )
	v.PrintInfo()
	v.Run()