#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
import sys
from flask import Flask
from models import app, db, Venue, Artist, Show 

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app.config.from_object('config')
moment = Moment(app)
db.init_app(app)

# TODO: connect to a local postgresql database (READY IN config.py)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
   

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format,locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  locals = []
  venues = Venue.query.all()
  places = Venue.query.distinct(Venue.city, Venue.state).all()
  for place in places:
      locals.append({
          'city': place.city,
          'state': place.state,
          'venues': [{
              'id': venue.id,
              'name': Venue.name,
          } for venue in venues if
              venue.city == place.city and venue.state == place.state]
      })
  return render_template('pages/venues.html', areas=locals)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  new_results = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = []

  for result in new_results:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == result.id).filter(Show.Start_Time > datetime.now()).all()),
    })
  
  response={
    "count": len(new_results),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venue = Venue.query.get(venue_id)

  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.Start_Time>datetime.now()).all()
  upcoming_shows = []

  past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.Start_Time<datetime.now()).all()
  past_shows = []

  for show in past_shows_query:
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.Artist.name,
      "artist_image_link": show.Artist.image_link,
      "Start_Time": show.Start_Time.strftime('%Y-%m-%d %H:%M:%S')
    })

  for show in upcoming_shows_query:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.Artist.name,
      "artist_image_link": show.Artist.image_link,
      "Start_Time": show.Start_Time.strftime("%Y-%m-%d %H:%M:%S")    
    })

  data_venue = {
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
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_venue.html', venue=data_venue)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!') (READY)
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')(READY)
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/ (READY)
def create_venue_submission():
  error = False
  form = VenueForm(request.form)
  try:
    new_venue = Venue()
    form.populate_obj(new_venue)
    db.session.add(new_venue)
    db.session.commit()
  except Exception as e: 
    error = True
    print(e)
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Venue ' + request.form['name']+ ' could not be listed.')
  if not error: 
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = Venue.query.first_or_404(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('The venue has been removed together with all of its shows.')
    return render_template('pages/home.html')
  except Exception as e:
    print("Soy el error")
    print(e)
    print("______________ ")
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash(f'Venue {venue_id} was successfully deleted.')
  finally:
    db.session.close()
  return redirect(url_for('venues'))

    


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.with_entities(Artist.id, Artist.name).order_by('id').all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  new_result = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = []

  for result in new_result:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == result.id).filter(Show.Start_Time > datetime.now()).all())
    })
  
  response={
    "count": len(new_result),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = db.session.query(Artist).get(artist_id)

  past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.Start_Time>datetime.now()).all()
  past_shows = []

  for show in past_shows_query:
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.Venue.name,
      "artist_image_link": show.Venue.image_link,
      "Start_Time": show.Start_Time.strftime('%Y-%m-%d %H:%M:%S')
    })

  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.Start_Time>datetime.now()).all()
  upcoming_shows = []

  for show in upcoming_shows_query:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.Venue.name,
      "artist_image_link": show.Venue.image_link,
      "Start_Time": show.Start_Time.strftime('%Y-%m-%d %H:%M:%S')
    })

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

    artist = Artist.query.filter(Artist.id == artist_id).first()

    # Fill form
    form = ArtistForm()
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.image_link.data = artist.image_link
    form.facebook_link.data = artist.facebook_link
    form.website.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      phone = request.form['phone']
      genres = request.form.getlist('genres')
      image_link = request.form['image_link']
      facebook_link = request.form['facebook_link']
      website = request.form['website']
      seeking_venue = True if 'seeking_talent' in request.form else False
      seeking_description = request.form['seeking_description']


      artist = Artist.query.get(artist_id)

      artist.name = name
      artist.city = city
      artist.state = state
      artist.phone = phone
      artist.genres = genres
      artist.image_link = image_link
      artist.facebook_link = facebook_link
      artist.website = website
      artist.seeking_venue = seeking_venue
      artist.seeking_description = seeking_description

      db.session.commit()
  except Exception as e:
      print(e)
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()

  if error:
      flash(
        'An error occurred. Artist '+ request.form['name']+ ' could not be updated.'
      )
  if not error:
      flash('Artist '+ request.form['name']+' was successfully updated!'
      )
  return redirect(url_for('show_artist', artist_id=artist_id))
  
@app.route('/artists/<artist_id>', methods=['POST'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    artist = Artist.query.first_or_404(artist_id)
    db.session.delete(artist)
    db.session.commit()
    flash('The artist has been removed together with all of its shows.')
    return render_template('pages/home.html')
  except Exception as e:
    print("Soy el error")
    print(e)
    print("______________ ")
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash(f'Artist {artist_id} was successfully deleted.')
  finally:
    db.session.close()
  return redirect(url_for('artists'))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  if venue: 
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False 
  try: 
    name = request.form['name']
    genres = request.form.getlist('genres')
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    website = request.form['website']
    facebook_link = request.form['facebook_link']
    seeking_talent = True if 'seeking_talent' in request.form else False
    seeking_description = request.form['seeking_description']
    image_link = request.form['image_link']
     
    venue = Venue.query.get(venue_id)

    venue.name = name
    venue.city = city
    venue.state = state
    venue.address = address
    venue.phone = phone
    venue.genres = genres
    venue.image_link = image_link
    venue.facebook_link =facebook_link
    venue.website = website
    venue.seeking_talent = seeking_talent 
    venue.seeking_description = seeking_description

    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash(f'An error occurred. Venue could not be changed.')
  if not error: 
    flash(f'Venue was successfully updated!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  form = ArtistForm(request.form)
  try:
    new_artist = Artist()
    form.populate_obj(new_artist)
    db.session.add(new_artist)
    db.session.commit()
  except Exception as e: 
    print(e)
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Artist ' + request.form['name']+' could not be listed.')
  if not error: 
    flash('Artist '+ request.form['name']+ ' was successfully listed!')
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')
  

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  showses= db.session.query(Show).join(Artist).join(Venue).all()
  for show in showses:
    data.append({
      'venue_name': show.Venue.name,
      'artist_name': show.Artist.name,
      'artist_image_link': show.Artist.image_link,
      'venue_id': show.venue_id,
      'artist_id': show.artist_id,
      'Start_Time': str(show.Start_Time)
  })

  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create', methods=['GET'])
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    Start_Time = request.form['Start_Time']

    new_show = Show(
      artist_id=artist_id,
      venue_id=venue_id,
      Start_Time=Start_Time
    )
    db.session.add(new_show)
    db.session.commit()
    
  except Exception as e:
      print(e)
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Show could not be listed.')
  if not error:
      flash('Show was successfully listed!')

  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
