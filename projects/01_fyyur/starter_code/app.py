#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from models import db, Artist, Venue, Shows

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app,db)



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')



#  Venues
#  ----------------------------------------------------------------

#  All venues 
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
  data = []
  distinctlocations = Venue.query.distinct(Venue.city,Venue.state).all()
  for location in distinctlocations:
    locationvenues = {
      "city" : location.city,
      "state" : location.state
    }
    
    venues = Venue.query.filter_by(city = location.city).filter_by(state = location.state).all()
    venueunit = []
    for venue in venues:
      venueunit.append({
        "id":venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), Shows.query.filter_by(venue_id=venue.id)))),
      })
    locationvenues['venues'] = venueunit
    data.append(locationvenues)

  return render_template('pages/venues.html', areas=data);


#  Search Venue
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term')
  resultingvenues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()  
  
  count = len(resultingvenues)
  print(count)
  response = {
    'count':count,
  }
  data = []
  for venue in resultingvenues:
    upcoming_shows = list(filter(lambda x: x.start_time > datetime.now(), Shows.query.filter_by(venue_id=venue.id)))  
    num_upcoming_shows = len(upcoming_shows)
    venuedetails = {
      'id':venue.id,
      'name':venue.name,
      'num_upcoming_shows':num_upcoming_shows,
    }
    data.append(venuedetails)
  response['data'] = data

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


#  Show Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):  
  venue = Venue.query.get(venue_id)
  
  past_shows = list(filter(lambda x: x.start_time < datetime.now(), Shows.query.filter_by(venue_id=venue.id)))
  past_shows_count = len(past_shows)  
  pastshow_store = []
  for past_show in past_shows:
    pastshowdets = {
      "artist_id":past_show.artist_id,
      "artist_name":Artist.query.get(past_show.artist_id).name,
      "artist_image_link":Artist.query.get(past_show.artist_id).image_link,
      "start_time":past_show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    }
    pastshow_store.append(pastshowdets)

  upcoming_shows = list(filter(lambda x: x.start_time > datetime.now(), Shows.query.filter_by(venue_id=venue.id)))  
  upcoming_shows_count = len(upcoming_shows)
  upcomingshow_store = []
  for upcoming_show in upcoming_shows:
    upcomingshowdets = {
      "artist_id":upcoming_show.artist_id,
      "artist_name":Artist.query.get(upcoming_show.artist_id).name,
      "artist_image_link":Artist.query.get(upcoming_show.artist_id).image_link,
      "start_time":upcoming_show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    }
    upcomingshow_store.append(upcomingshowdets)

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": pastshow_store,
    "upcoming_shows": upcomingshow_store,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count":upcoming_shows_count,
  }  
  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  named = request.form.get('name')
  seeking_talent = True if request.form.get('seeking_talent') else False
  try:
    new_venue = Venue(
    name = named,
    city = request.form.get('city'),
    state = request.form.get('state'),
    address = request.form.get('address'),
    phone = request.form.get('phone'),
    genres = request.form.getlist('genres'),
    facebook_link = request.form.get('facebook_link'),
    image_link = request.form.get('image_link'),
    website = request.form.get('website_link'),
    seeking_talent = seeking_talent,
    seeking_description = request.form.get('seeking_description'),
    )

    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + named + ' was successfully listed!')

  except:    
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + named + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None




#  Artists
#  ----------------------------------------------------------------

#  show all artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = []
  for artist in artists:
    artistidentity = {
      'id': artist.id,
      'name':artist.name
    }
    data.append(artistidentity)

  return render_template('pages/artists.html', artists=data)


#  Search Artists
#  ----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term')
  resultingartists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()  
  
  count = len(resultingartists)
  print(count)
  response = {
    'count':count,
  }
  data = []
  for artist in resultingartists:
    upcoming_shows = list(filter(lambda x: x.start_time > datetime.now(), Shows.query.filter_by(artist_id=artist.id)))  
    num_upcoming_shows = len(upcoming_shows)
    artistdetails = {
      'id':artist.id,
      'name':artist.name,
      'num_upcoming_shows':num_upcoming_shows,
    }
    data.append(artistdetails)
  response['data'] = data

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


# Show Artists
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)

  past_shows = list(filter(lambda x: x.start_time < datetime.now(), Shows.query.filter_by(artist_id=artist.id)))
  past_shows_count = len(past_shows)  
  pastshow_store = []
  for past_show in past_shows:
    pastshowdets = {
      "venue_id":past_show.venue_id,
      "venue_name":Venue.query.get(past_show.venue_id).name,
      "venue_image_link":Venue.query.get(past_show.venue_id).image_link,
      "start_time":past_show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    }
    pastshow_store.append(pastshowdets)

  upcoming_shows = list(filter(lambda x: x.start_time > datetime.now(), Shows.query.filter_by(artist_id=artist.id)))
  upcoming_shows_count = len(upcoming_shows)  
  upcomingshow_store = []
  for upcoming_show in upcoming_shows:
    upcomingshowdets = {
      "venue_id":upcoming_show.venue_id,
      "venue_name":Venue.query.get(upcoming_show.venue_id).name,
      "venue_image_link":Venue.query.get(upcoming_show.venue_id).image_link,
      "start_time":upcoming_show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    }
    upcomingshow_store.append(upcomingshowdets)

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": pastshow_store,
    "upcoming_shows": upcomingshow_store,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count
  }

  return render_template('pages/show_artist.html', artist=data)

#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  named = request.form.get('name')
  seeking_venue = True if request.form.get('seeking_venue') else False
  try:
    new_artist = Artist(
    name = request.form.get('name'),
    city = request.form.get('city'),
    state = request.form.get('state'),
    phone = request.form.get('phone'),
    genres = request.form.getlist('genres'),
    facebook_link = request.form.get('facebook_link'),
    image_link = request.form.get('image_link'),
    website = request.form.get('website_link'),
    seeking_venue = seeking_venue,
    seeking_description = request.form.get('seeking_description'),
    )

    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except:    
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + named + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')



#  Update
#  ----------------------------------------------------------------

#  Edit Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  art = Artist.query.get(artist_id)
  artist={
    "id": art.id,
    "name": art.name,
    "genres": art.genres,
    "city": art.city,
    "state": art.state,
    "phone": art.phone,
    "website": art.website,
    "facebook_link": art.facebook_link,
    "seeking_venue": art.seeking_venue,
    "seeking_description": art.seeking_description,
    "image_link": art.image_link,
  }
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  seeking_venue = True if request.form.get('seeking_venue') else False
  try:
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form.get('facebook_link')
    artist.image_link = request.form.get('image_link')
    artist.website = request.form.get('website_link')
    artist.seeking_venue = seeking_venue
    artist.seeking_description = request.form.get('seeking_description')

    db.session.commit()
    flash("Artist " + artist.name + " was successfully edited!")

  except:
    db.session.rollback()
    print(sys.exc_info())
    flash("Artist was not edited successfully.")
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))


# Edit Venues
#  ---------------------------------------------------------------- 
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue=Venue.query.get(venue_id)
  seeking_talent = True if request.form.get('seeking_talent') else False    

  try:
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form.get('facebook_link')
    venue.image_link = request.form.get('image_link')
    venue.website = request.form.get('website_link')
    venue.seeking_talent = seeking_talent
    venue.seeking_description = request.form.get('seeking_description')

    db.session.commit()
    flash("Venue " + venue.name + " edited successfully")
  
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash(Venue.name + " was not edited successfully.")

  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))



#  Shows
#  ----------------------------------------------------------------


# Display all shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  shows = Shows.query.all()
  venue = Venue.query.all()
  artist = Artist.query.all()
  data = []
  for show in shows:
    showdetails = {
      "venue_id": show.venue_id,
      "venue_name":Venue.query.get(show.venue_id).name,
      "artist_id":show.artist_id,
      "artist_name":Artist.query.get(show.artist_id).name,
      "artist_image_link": Artist.query.get(show.artist_id).image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    }
    data.append(showdetails)

  return render_template('pages/shows.html', shows=data)


#  Create Shows
#  ----------------------------------------------------------------
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  artistidea = request.form.get('venue_id')
  try:
    new_show = Shows(
      artist_id = request.form.get('artist_id'),
      venue_id = request.form.get('venue_id'),
      start_time = request.form.get('start_time')
    )

    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')

  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
    
  finally:
    db.session.close()

  return render_template('pages/home.html')



@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
