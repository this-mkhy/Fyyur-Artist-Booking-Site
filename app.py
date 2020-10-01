#----------------------------------------------------------------------------#
# Imports
# https://www.codementor.io/@sheena/understanding-sqlalchemy-cheat-sheet-du107lawl
# https://s3.us-east-2.amazonaws.com/prettyprinted/flask_cheatsheet.pdf
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import exc

from datetime import datetime
import re
from operator import itemgetter 
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# define migrate
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# defined the models and relations
# the Genre table here 
class Genre(db.Model):
    __tablename__ = 'Genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

artist_genre_table = db.Table('artist_genre_table',
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
)

venue_genre_table = db.Table('venue_genre_table',
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
)
    
    
# Venue is the parent (one-to-many) of a Show (Artist is also a foreign key, in def. of Show)
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.relationship('Genre', secondary=venue_genre_table, backref=db.backref('venues'))

    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))

    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

# Artist is the parent (one-to-many) of a Show (Venue is also a foreign key, in def. of Show)
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.relationship('Genre', secondary=artist_genre_table, backref=db.backref('artists'))

    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))

    shows = db.relationship('Show', backref='artist', lazy=True)   

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)   

    # Foreign key is the tablename.pk
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)   
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

    def __repr__(self):
        return f'<Show {self.id} {self.start_time} artist_id={artist_id} venue_id={venue_id}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)
# this filter helper that used at the show page. It makes it user interactivity interesting.
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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # data = [{
  #     "city": "San Francisco",
  #     "state": "CA",
  #     "venues": [{
  #         "id": 1,
  #         "name": "The Musical Hop",
  #         "num_upcoming_shows": 0,
  #     }, {
  #         "id": 3,
  #         "name": "Park Square Live Music & Coffee",
  #         "num_upcoming_shows": 1,
  #     }]
  # }, {
  #     "city": "New York",
  #     "state": "NY",
  #     "venues": [{
  #         "id": 2,
  #         "name": "The Dueling Pianos Bar",
  #         "num_upcoming_shows": 0,
  #     }]
  # }]

  # venues = Venue.query.order_by(Venue.state, Venue.city.asc()).all()
  venues = Venue.query.all()

  data = [] 

  # Set of all the cities_states
  cities_states = set()
  for venue in venues:
      cities_states.add( (venue.city, venue.state) )  
  
  cities_states = list(cities_states)
  cities_states.sort(key=itemgetter(1,0))    

  now = datetime.now()

  for loc in cities_states:
      venues_list = []
      for venue in venues:
          if (venue.city == loc[0]) and (venue.state == loc[1]):

              # If we have a venue to add, check how many upcoming shows it has
              venue_shows = Show.query.filter_by(venue_id=venue.id).all()
              num_upcoming = 0
              for show in venue_shows:
                  if show.start_time > now:
                      num_upcoming += 1

              venues_list.append({
                  "id": venue.id,
                  "name": venue.name,
                  "num_upcoming_shows": num_upcoming
              })

      # After all venues are added to the list for a given location, add it to our data dictionary
      data.append({
          "city": loc[0],
          "state": loc[1],
          "venues": venues_list
      })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '').strip()

  # using ilike operator instead of like operator to match case insensitive
  venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all() 
  print(venues)
  venue_list = []
  now = datetime.now()
  for venue in venues:
      venue_shows = Show.query.filter_by(venue_id=venue.id).all()
      num_upcoming = 0
      for show in venue_shows:
          if show.start_time > now:
              num_upcoming += 1

      venue_list.append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": num_upcoming
      })

  response = {
      "count": len(venues),
      "data": venue_list
  }

  # response = {
  #     "count": 1,
  #     "data": [{
  #         "id": 2,
  #         "name": "The Dueling Pianos Bar",
  #         "num_upcoming_shows": 0,
  #     }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)   
  print(venue)
  if not venue:
    # Redirect home
    return redirect(url_for('index'))
  else:
    genres = [ genre.name for genre in venue.genres ]
    
    # Get a list of shows and count the ones in the past and future
    past_shows = []
    past_shows_count = 0
    upcoming_shows = []
    upcoming_shows_count = 0
    now = datetime.now()
    for show in venue.shows:
        if show.start_time > now:
            upcoming_shows_count += 1
            upcoming_shows.append({
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": format_datetime(str(show.start_time))
            })
        if show.start_time < now:
            past_shows_count += 1
            past_shows.append({
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": format_datetime(str(show.start_time))
            })

    data = {
        "id": venue_id,
        "name": venue.name,
        "genres": genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": (venue.phone[:3] + '-' + venue.phone[3:6] + '-' + venue.phone[6:]),
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows": upcoming_shows,
        "upcoming_shows_count": upcoming_shows_count
    }

  # data1 = {
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #     "address": "1015 Folsom Street",
  #     "city": "San Francisco",
  #     "state": "CA",
  #     "phone": "123-123-1234",
  #     "website": "https://www.themusicalhop.com",
  #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #     "seeking_talent": True,
  #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "past_shows": [{
  #         "artist_id": 4,
  #         "artist_name": "Guns N Petals",
  #         "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #         "start_time": "2019-05-21T21:30:00.000Z"
  #     }],
  #     "upcoming_shows": [],
  #     "past_shows_count": 1,
  #     "upcoming_shows_count": 0,
  # }

  # data = list(filter(lambda d: d['id'] ==
  #                    venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()

  name = form.name.data.strip()
  city = form.city.data.strip()
  state = form.state.data
  address = form.address.data.strip()
  phone = form.phone.data
  phone = re.sub('\D', '', phone) 
  genres = form.genres.data
  seeking_talent = True if form.seeking_talent.data == 'Yes' else False
  seeking_description = form.seeking_description.data.strip()
  image_link = form.image_link.data.strip()
  website = form.website.data.strip()
  facebook_link = form.facebook_link.data.strip()
  
  # Redirect back to form if errors in form validation
  if not form.validate():
    flash( form.errors )
    return redirect(url_for('create_venue_submission'))

  else:
      error_in_insert = False

      # Insert data into DB
      try:
          # creates the new venue with all fields
          new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone, \
              seeking_talent=seeking_talent, seeking_description=seeking_description, image_link=image_link, \
              website=website, facebook_link=facebook_link)
          for genre in genres:
              # Throws an exception if more than one returned, returns None if none
              fetch_genre = Genre.query.filter_by(name=genre).one_or_none() 
              if fetch_genre:
                  # if found a genre, append it to the list
                  new_venue.genres.append(fetch_genre)
              else:
                  new_genre = Genre(name=genre)
                  db.session.add(new_genre)
                  # Create a new Genre item and append it
                  new_venue.genres.append(new_genre)  
          db.session.add(new_venue)
          db.session.commit()
      except Exception as e:
          error_in_insert = True
          print(f'Exception "{e}" in create_venue_submission()')
          db.session.rollback()
      finally:
          db.session.close()

      if not error_in_insert:
          # on successful db insert, flash success
          flash('Venue ' + request.form['name'] + ' was successfully listed!')
          return redirect(url_for('index'))
      else:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Venue ' + name + ' could not be listed.')
        print("Error in create_venue_submission()")
        # return redirect(url_for('create_venue_submission'))
        abort(500)

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  venue = Venue.query.get(venue_id)
  if not venue:
    return redirect(url_for('index'))
  else:
    error_on_delete = False
    venue_name = venue.name
    try:
      db.session.delete(venue)
      db.session.commit()
    except:
      error_on_delete = True
      db.session.rollback()
    finally:
      db.session.close()
    if error_on_delete:
      flash(f'An error occurred deleting venue {venue_name}.')
      print("Error in delete_venue()")
      abort(500)
    else:
      return jsonify({
        'deleted': True,
        'url': url_for('venues')
      })


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.order_by(Artist.name).all()  

  data = []
  for artist in artists:
    data.append({
        "id": artist.id,
        "name": artist.name
    })

  # data = [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  # }, {
  #     "id": 5,
  #     "name": "Matt Quevedo",
  # }, {
  #     "id": 6,
  #     "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_term = request.form.get('search_term', '').strip()
  artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()  
  
  print(artists)
  artist_list = []
  now = datetime.now()
  for artist in artists:
    artist_shows = Show.query.filter_by(artist_id=artist.id).all()
    num_upcoming = 0
    for show in artist_shows:
      if show.start_time > now:
        num_upcoming += 1

    artist_list.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming 
    })

  response = {
    "count": len(artists),
    "data": artist_list
  }

  # response={
  #  "count": 1,
  #  "data": [{
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "num_upcoming_shows": 0,
  #  }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  # Displays the artist page with the given artist_id.
  artist = Artist.query.get(artist_id)
  print(artist)
  if not artist:
    # Redirect home
    return redirect(url_for('index'))
  else:
    genres = [ genre.name for genre in artist.genres ]
    # Get a list of shows and count the ones in the past and future
    past_shows = []
    past_shows_count = 0
    upcoming_shows = []
    upcoming_shows_count = 0
    now = datetime.now()
    for show in artist.shows:
      if show.start_time > now:
        upcoming_shows_count += 1
        upcoming_shows.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": format_datetime(str(show.start_time))
        })
      if show.start_time < now:
        past_shows_count += 1
        past_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": format_datetime(str(show.start_time))
        })

    data = {
      "id": artist_id,
      "name": artist.name,
      "genres": genres,
      "city": artist.city,
      "state": artist.state,
      "phone": (artist.phone[:3] + '-' + artist.phone[3:6] + '-' + artist.phone[6:]),
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": past_shows,
      "past_shows_count": past_shows_count,
      "upcoming_shows": upcoming_shows,
      "upcoming_shows_count": upcoming_shows_count
    }

  # data1 = {
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "genres": ["Rock n Roll"],
  #     "city": "San Francisco",
  #     "state": "CA",
  #     "phone": "326-123-5000",
  #     "website": "https://www.gunsnpetalsband.com",
  #     "facebook_link": "https://www.facebook.com/GunsNPetals",
  #     "seeking_venue": True,
  #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "past_shows": [{
  #         "venue_id": 1,
  #         "venue_name": "The Musical Hop",
  #         "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #         "start_time": "2019-05-21T21:30:00.000Z"
  #     }],
  #     "upcoming_shows": [],
  #     "past_shows_count": 1,
  #     "upcoming_shows_count": 0,
  # }

  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # form = ArtistForm()
  # artist = {
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "genres": ["Rock n Roll"],
  #     "city": "San Francisco",
  #     "state": "CA",
  #     "phone": "326-123-5000",
  #     "website": "https://www.gunsnpetalsband.com",
  #     "facebook_link": "https://www.facebook.com/GunsNPetals",
  #     "seeking_venue": True,
  #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }

  # TODO: populate form with fields from artist with ID <artist_id>
  # Get the existing artist from the database
  artist = Artist.query.get(artist_id)  
  if not artist:
      # redirect home
      return redirect(url_for('index'))
  else:
      # Valid artist.. Prepopulate the form with the current values.
      form = ArtistForm(obj=artist)

  genres = [ genre.name for genre in artist.genres ]
  
  artist = {
      "id": artist_id,
      "name": artist.name,
      "genres": genres,
      "city": artist.city,
      "state": artist.state,
      "phone": (artist.phone[:3] + '-' + artist.phone[3:6] + '-' + artist.phone[6:]),
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link
  }
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()

  name = form.name.data.strip()
  city = form.city.data.strip()
  state = form.state.data
  phone = form.phone.data
  phone = re.sub('\D', '', phone) 
  genres = form.genres.data    
  seeking_venue = True if form.seeking_venue.data == 'Yes' else False
  seeking_description = form.seeking_description.data.strip()
  image_link = form.image_link.data.strip()
  website = form.website.data.strip()
  facebook_link = form.facebook_link.data.strip()
  
  if not form.validate():
    flash( form.errors )
    return redirect(url_for('edit_artist_submission', artist_id=artist_id))

  else:
    error_in_update = False
    # Insert form data into DB
    try:
      # First get the existing artist object
      artist = Artist.query.get(artist_id)

      # Update
      artist.name = name
      artist.city = city
      artist.state = state
      artist.phone = phone
      artist.seeking_venue = seeking_venue
      artist.seeking_description = seeking_description
      artist.image_link = image_link
      artist.website = website
      artist.facebook_link = facebook_link

      # Clear all the existing genres off the artist .. or artist.genres.clear()  
      # artist.genres.clear()  
      artist.genres = []
      
      for genre in genres:
        fetch_genre = Genre.query.filter_by(name=genre).one_or_none()  
        if fetch_genre:
          artist.genres.append(fetch_genre)
        else:
          new_genre = Genre(name=genre)
          db.session.add(new_genre)
          artist.genres.append(new_genre) 
      db.session.commit()
    except Exception as e:
      error_in_update = True
      print(f'Exception "{e}" in edit_artist_submission()')
      db.session.rollback()
    finally:
      db.session.close()

    if not error_in_update:
      # on successful db update, flash success
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
      return redirect(url_for('show_artist', artist_id=artist_id))
    else:
      flash('An error occurred. Artist ' + name + ' could not be updated.')
      print("Error in edit_artist_submission()")
      abort(500)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>

  # Get the existing venue from the database
  venue = Venue.query.get(venue_id)
  if not venue:
    # redirect home
    return redirect(url_for('index'))
  else:
    # Valid venue
    form = VenueForm(obj=venue)

  genres = [ genre.name for genre in venue.genres ]

  venue = {
    "id": venue_id,
    "name": venue.name,
    "genres": genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": (venue.phone[:3] + '-' + venue.phone[3:6] + '-' + venue.phone[6:]),
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }

  # venue = {
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #     "address": "1015 Folsom Street",
  #     "city": "San Francisco",
  #     "state": "CA",
  #     "phone": "123-123-1234",
  #     "website": "https://www.themusicalhop.com",
  #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #     "seeking_talent": True,
  #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()

  name = form.name.data.strip()
  city = form.city.data.strip()
  state = form.state.data
  address = form.address.data.strip()
  phone = form.phone.data
  phone = re.sub('\D', '', phone) 
  genres = form.genres.data 
  seeking_talent = True if form.seeking_talent.data == 'Yes' else False
  seeking_description = form.seeking_description.data.strip()
  image_link = form.image_link.data.strip()
  website = form.website.data.strip()
  facebook_link = form.facebook_link.data.strip()
  
  # Redirect back to the form if errors in form validation
  if not form.validate():
    flash( form.errors )
    return redirect(url_for('edit_venue_submission', venue_id=venue_id))

  else:
    error_in_update = False

    # Insert form data into DB
    try:
      venue = Venue.query.get(venue_id)
      # venue = Venue.query.filter_by(id=venue_id).one_or_none()

      # Update
      venue.name = name
      venue.city = city
      venue.state = state
      venue.address = address
      venue.phone = phone
      venue.seeking_talent = seeking_talent
      venue.seeking_description = seeking_description
      venue.image_link = image_link
      venue.website = website
      venue.facebook_link = facebook_link

      # Clear all the existing genres off the venue ... OR => venue.genres.clear()
      # venue.genres.clear()
      venue.genres = []
      
      for genre in genres:
        fetch_genre = Genre.query.filter_by(name=genre).one_or_none() 
        if fetch_genre:
          venue.genres.append(fetch_genre)
        else:
          new_genre = Genre(name=genre)
          db.session.add(new_genre)
          venue.genres.append(new_genre)  
      db.session.commit()
    except Exception as e:
      error_in_update = True
      print(f'Exception "{e}" in edit_venue_submission()')
      db.session.rollback()
    finally:
      db.session.close()

    if not error_in_update:
      # on successful db update, flash success
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
      return redirect(url_for('show_venue', venue_id=venue_id))
    else:
      flash('An error occurred. Venue ' + name + ' could not be updated.')
      print("Error in edit_venue_submission()")
      abort(500)

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
  form = ArtistForm()

  name = form.name.data.strip()
  city = form.city.data.strip()
  state = form.state.data
  phone = form.phone.data
  phone = re.sub('\D', '', phone) 
  genres = form.genres.data
  seeking_venue = True if form.seeking_venue.data == 'Yes' else False
  seeking_description = form.seeking_description.data.strip()
  image_link = form.image_link.data.strip()
  website = form.website.data.strip()
  facebook_link = form.facebook_link.data.strip()
  
  # Redirect back to the form if errors in form validation
  if not form.validate():
    flash( form.errors )
    return redirect(url_for('create_artist_submission'))

  else:
    error_in_insert = False

    # Insert form data into DB
    try:
        # creates the new artist
        new_artist = Artist(name=name, city=city, state=state, phone=phone, \
          seeking_venue=seeking_venue, seeking_description=seeking_description, image_link=image_link, \
          website=website, facebook_link=facebook_link)
        for genre in genres:
          fetch_genre = Genre.query.filter_by(name=genre).one_or_none()
          if fetch_genre:
            new_artist.genres.append(fetch_genre)

          else:
            new_genre = Genre(name=genre)
            db.session.add(new_genre)
            new_artist.genres.append(new_genre)
        db.session.add(new_artist)
        db.session.commit()
    except Exception as e:
      error_in_insert = True
      print(f'Exception "{e}" in create_artist_submission()')
      db.session.rollback()
    finally:
      db.session.close()

    # validating input
    if not error_in_insert:
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return redirect(url_for('index'))
    else:
      flash('An error occurred. Artist ' + name + ' could not be listed.')
      print("Error in create_artist_submission()")
      abort(500)

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


@app.route('/artists/<artist_id>/delete', methods=['GET'])
def delete_artist(artist_id):
  # TODO: delete form data of artist as a new Venue record in the db

  # Deletes a artist based on AJAX call from the artist page
  artist = Artist.query.get(artist_id)
  if not artist:
    # redirect home
    return redirect(url_for('index'))
  else:
    error_on_delete = False
    artist_name = artist.name
    try:
      db.session.delete(artist)
      db.session.commit()
    except:
      error_on_delete = True
      db.session.rollback()
    finally:
      db.session.close()
    if error_on_delete:
      flash(f'An error occurred deleting artist {artist_name}.')
      print("Error in delete_artist()")
      abort(500)
    else:
      # return redirect(url_for('artists'))
      return jsonify({
        'deleted': True,
        'url': url_for('artists')
      })

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = Show.query.all()
  
  for show in shows:
    data.append({
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.start_time))
    })
  # data = [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  # }]
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
  form = ShowForm()

  artist_id = form.artist_id.data.strip()
  venue_id = form.venue_id.data.strip()
  start_time = form.start_time.data

  error_in_insert = False
  
  try:
    new_show = Show(start_time=start_time, artist_id=artist_id, venue_id=venue_id)
    db.session.add(new_show)
    db.session.commit()
  except:
    error_in_insert = True
    print(f'Exception "{e}" in create_show_submission()')
    db.session.rollback()
  finally:
    db.session.close()

  if error_in_insert:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash(f'An error occurred.  Show could not be listed.')
    print("Error in create_show_submission()")
  else:
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  return render_template('pages/home.html')

# handling 404 ad 500 errors to display more specific messages to users on what exactly happened
# not_found - 404
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

# server_error - 500
@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

# # unauthorized - 401
# @app.errorhandler(401)
# def server_error(error):
#     return render_template('errors/401.html'), 401
    
# # forbidden - 403
# @app.errorhandler(403)
# def server_error(error):
#     return render_template('errors/403.html'), 403

# # not_processable - 422
# @app.errorhandler(422)
# def server_error(error):
#     return render_template('errors/422.html'), 422

# # invalid_method - 405
# @app.errorhandler(405)
# def server_error(error):
#     return render_template('errors/405.html'), 405

# # duplicate_resource - 409
# @app.errorhandler(409)
# def server_error(error):
#     return render_template('errors/409.html'), 409

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
