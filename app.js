const express = require('express');
const path = require('path');
const https = require('https');
const session = require('express-session');
const passport = require('passport');
const bodyParser = require('body-parser');
const dotenv = require('dotenv');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const MicrosoftStrategy = require('passport-microsoft').Strategy;

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

const users = [];

function findUserByEmail(email) {
  return users.find((user) => user.email.toLowerCase() === email.toLowerCase());
}

function createUser(user) {
  users.push(user);
  return user;
}

function fetchJson(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          if (res.statusCode && res.statusCode >= 400) {
            return reject(new Error(`Weather API error ${res.statusCode}`));
          }
          resolve(json);
        } catch (error) {
          reject(error);
        }
      });
    }).on('error', reject);
  });
}

function getPrecipitationProbability(hourly, currentTime) {
  const times = hourly.time || [];
  let index = times.length - 1;
  while (index >= 0 && times[index] > currentTime) {
    index -= 1;
  }
  if (index >= 0) {
    return hourly.precipitation_probability[index];
  }
  return null;
}

async function getWeatherData() {
  const tempUnit = 'fahrenheit';
  const url = `https://api.open-meteo.com/v1/forecast?latitude=41.137&longitude=-77.4469&hourly=temperature_2m,precipitation_probability,precipitation,apparent_temperature&current=temperature_2m,apparent_temperature,precipitation,rain,showers,snowfall&timezone=America%2FNew_York&temperature_unit=${tempUnit}`;
  try {
    const response = await fetchJson(url);
    const current = response.current;
    const hourly = response.hourly;
    if (!current || !hourly || !hourly.time || !hourly.precipitation_probability) {
      return null;
    }
    const precipitationProbability = getPrecipitationProbability(hourly, current.time);
    return {
      temperature: current.temperature_2m,
      apparentTemperature: current.apparent_temperature,
      precipitationProbability: precipitationProbability != null ? precipitationProbability : 'N/A',
      unit: tempUnit === 'fahrenheit' ? '°F' : '°C'
    };
  } catch (error) {
    console.error('Weather fetch failed:', error.message);
    return null;
  }
}

passport.serializeUser((user, done) => {
  done(null, user.email);
});

passport.deserializeUser((email, done) => {
  const user = findUserByEmail(email);
  done(null, user || false);
});

passport.use(new GoogleStrategy({
  clientID: process.env.GOOGLE_CLIENT_ID || 'GOOGLE_CLIENT_ID',
  clientSecret: process.env.GOOGLE_CLIENT_SECRET || 'GOOGLE_CLIENT_SECRET',
  callbackURL: '/auth/google/callback'
}, (accessToken, refreshToken, profile, done) => {
  const email = profile.emails && profile.emails[0] && profile.emails[0].value;
  if (!email) {
    return done(new Error('Google profile did not contain an email'));
  }
  let user = findUserByEmail(email);
  if (!user) {
    user = createUser({
      email,
      displayName: profile.displayName || email,
      provider: 'google',
      id: profile.id
    });
  }
  done(null, user);
}));

passport.use(new MicrosoftStrategy({
  clientID: process.env.MICROSOFT_CLIENT_ID || 'MICROSOFT_CLIENT_ID',
  clientSecret: process.env.MICROSOFT_CLIENT_SECRET || 'MICROSOFT_CLIENT_SECRET',
  callbackURL: '/auth/microsoft/callback',
  scope: ['openid', 'profile', 'email', 'User.Read']
}, (accessToken, refreshToken, profile, done) => {
  const email = profile.emails && profile.emails[0] && profile.emails[0].value;
  const fallbackEmail = profile._json && profile._json.userPrincipalName;
  const finalEmail = email || fallbackEmail;

  if (!finalEmail) {
    return done(new Error('Microsoft profile did not contain an email'));
  }
  let user = findUserByEmail(finalEmail);
  if (!user) {
    user = createUser({
      email: finalEmail,
      displayName: profile.displayName || finalEmail,
      provider: 'microsoft',
      id: profile.id
    });
  }
  done(null, user);
}));

app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');

app.use(express.static(path.join(__dirname, 'public')));
app.use(bodyParser.urlencoded({ extended: false }));
app.use(session({
  secret: process.env.SESSION_SECRET || 'change-this-secret',
  resave: false,
  saveUninitialized: false
}));
app.use(passport.initialize());
app.use(passport.session());
app.use((req, res, next) => {
  res.locals.user = req.user;
  next();
});

function ensureAuthenticated(req, res, next) {
  if (req.isAuthenticated()) {
    return next();
  }
  res.redirect('/signin');
}

app.get('/', (req, res) => {
  res.redirect('/dashboard');
});

app.get('/signin', (req, res) => {
  res.render('signin', { user: req.user, error: req.query.error });
});

app.post('/signin', (req, res) => {
  const { email, password } = req.body;
  const user = findUserByEmail(email || '');
  if (!user || user.password !== password) {
    return res.redirect('/signin?error=Invalid+email+or+password');
  }
  req.login(user, (err) => {
    if (err) {
      return res.redirect('/signin?error=Login+failed');
    }
    res.redirect('/dashboard');
  });
});

app.get('/signup', (req, res) => {
  res.render('signup', { user: req.user, error: req.query.error });
});

app.post('/signup', (req, res) => {
  const { email, password, displayName } = req.body;
  if (!email || !password) {
    return res.redirect('/signup?error=Email+and+password+are+required');
  }
  if (findUserByEmail(email)) {
    return res.redirect('/signup?error=Email+already+registered');
  }
  const user = createUser({
    email,
    password,
    displayName: displayName || email,
    provider: 'local'
  });
  req.login(user, (err) => {
    if (err) {
      return res.redirect('/signup?error=Sign+up+failed');
    }
    res.redirect('/dashboard');
  });
});

app.get('/dashboard', async (req, res) => {
  const weather = await getWeatherData();
  res.render('dashboard', { user: req.user, weather });
});

app.get('/api/date', (req, res) => {
  res.json({ date: new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) });
});

app.get('/logout', (req, res) => {
  req.logout(() => {
    res.redirect('/dashboard');
  });
});

app.get('/auth/google', passport.authenticate('google', { scope: ['profile', 'email'] }));
app.get('/auth/google/callback', passport.authenticate('google', {
  failureRedirect: '/signin?error=Google+login+failed'
}), (req, res) => {
  res.redirect('/dashboard');
});

app.get('/auth/microsoft', passport.authenticate('microsoft'));
app.get('/auth/microsoft/callback', passport.authenticate('microsoft', {
  failureRedirect: '/signin?error=Microsoft+login+failed'
}), (req, res) => {
  res.redirect('/dashboard');
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
