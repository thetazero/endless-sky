/* Effect.h
Copyright (c) 2014 by Michael Zahniser

Endless Sky is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Endless Sky is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.
*/

#ifndef EFFECT_H_
#define EFFECT_H_

#include "Angle.h"
#include "Body.h"
#include "Point.h"

#include <string>

class DataNode;
class Sound;



// Class representing a graphic such as an explosion which is drawn for effect but
// has no impact on any other objects in the game.
class Effect : public Body {
public:
	/* Functions provided by the Body base class:
	Frame GetFrame(int step = -1) const;
	const Point &Position() const;
	const Point &Velocity() const;
	const Angle &Facing() const;
	Point Unit() const;
	double Zoom() const;
	*/
	
	const std::string &Name() const;
	
	void Load(const DataNode &node);
	// If creating a new effect, the animation and lifetime are copied,
	// but position, velocity, and angle are specific to this new effect.
	void Place(Point pos, Point vel, Angle facing, Point hitVelocity = Point());
	
	// Step the effect forward.
	void Move();
	
	
private:
	std::string name;
	
	const Sound *sound = nullptr;
	
	Angle spin;
	
	// Parameters used for randomizing spin and velocity. The random angle is
	// added to the parent angle, and then a random velocity in that direction
	// is added to the parent velocity.
	double velocityScale = 1.;
	double randomVelocity = 0.;
	double randomAngle = 0.;
	double randomSpin = 0.;
	double randomFrameRate = 0.;
	
	int lifetime = 0;
};



#endif
