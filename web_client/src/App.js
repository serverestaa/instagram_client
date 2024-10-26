import React, { useState, useEffect } from 'react';
import { Button, Modal, Input, Menu, MenuItem, Avatar } from '@mui/material';
import { makeStyles } from '@mui/styles';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import './App.css';
import Post from './Post';
import ImageUpload from './ImageUpload';
import Profile from './Profile';

const BASE_URL = 'http://localhost:8000/';

function getModalStyle() {
  const top = 50;
  const left = 50;

  return {
    top: `${top}%`,
    left: `${left}%`,
    transform: `translate(-${top}%, -${left}%)`,
  };
}

const useStyles = makeStyles((theme) => ({
  paper: {
    backgroundColor: theme.palette.background.paper || '#fff',
    position: 'absolute',
    width: 400,
    border: '2px solid #000',
    boxShadow: theme.shadows[5],
    padding: theme.spacing(2, 4, 3),
  },
}));

function App() {
  const classes = useStyles();
  const [posts, setPosts] = useState([]);
  const [openSignIn, setOpenSignIn] = useState(false);
  const [openSignUp, setOpenSignUp] = useState(false);
  const [modalStyle] = useState(getModalStyle);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [authToken, setAuthToken] = useState(null);
  const [authTokenType, setAuthTokenType] = useState(null);
  const [userId, setUserId] = useState('');
  const [email, setEmail] = useState('');

  // State for profile menu
  const [anchorEl, setAnchorEl] = useState(null);

  useEffect(() => {
    setAuthToken(window.localStorage.getItem('authToken'));
    setAuthTokenType(window.localStorage.getItem('authTokenType'));
    setUsername(window.localStorage.getItem('username'));
    setUserId(window.localStorage.getItem('userId'));
  }, []);

  useEffect(() => {
    authToken
      ? window.localStorage.setItem('authToken', authToken)
      : window.localStorage.removeItem('authToken');
    authTokenType
      ? window.localStorage.setItem('authTokenType', authTokenType)
      : window.localStorage.removeItem('authTokenType');
    username
      ? window.localStorage.setItem('username', username)
      : window.localStorage.removeItem('username');
    userId
      ? window.localStorage.setItem('userId', userId)
      : window.localStorage.removeItem('userId');
  }, [authToken, authTokenType, username, userId]);

  useEffect(() => {
    fetch(BASE_URL + 'post/all')
      .then((response) => {
        if (!response.ok) throw new Error('Failed to fetch posts');
        return response.json();
      })
      .then((data) => {
        const sortedPosts = data.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        setPosts(sortedPosts);
      })
      .catch((error) => {
        console.error(error);
        alert('Error fetching posts');
      });
  }, []);

  const signIn = (event) => {
    event?.preventDefault();
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    fetch(BASE_URL + 'login', { method: 'POST', body: formData })
      .then((response) => {
        if (!response.ok) throw new Error('Failed to sign in');
        return response.json();
      })
      .then((data) => {
        setAuthToken(data.access_token);
        setAuthTokenType(data.token_type);
        setUserId(data.user_id);
        setUsername(data.username);
        setOpenSignIn(false);
      })
      .catch((error) => {
        console.error(error);
        alert('Sign in failed');
      });
  };

  const signOut = () => {
    setAuthToken(null);
    setAuthTokenType(null);
    setUserId('');
    setUsername('');
    setAnchorEl(null);
  };

  const signUp = (event) => {
    event?.preventDefault();
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }),
    };

    fetch(BASE_URL + 'user/', requestOptions)
      .then((response) => {
        if (!response.ok) throw new Error('Failed to sign up');
        return response.json();
      })
      .then(() => {
        signIn();
        setOpenSignUp(false);
      })
      .catch((error) => {
        console.error(error);
        alert('Sign up failed');
      });
  };

  const handleProfileMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleCloseMenu = () => {
    setAnchorEl(null);
  };

  return (
    <Router>
      <div className="app">
        <Modal open={openSignIn} onClose={() => setOpenSignIn(false)}>
          <div style={modalStyle} className={classes.paper}>
            <form className="app_signin">
              <center>
                <img
                  className="app_signinImage"
                  src="https://www.virtualstacks.com/wp-content/uploads/2019/11/instagram-logo-name.png"
                  alt="Instagram"
                />
              </center>
              <Input placeholder="username" type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
              <Input placeholder="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
              <Button type="submit" onClick={signIn}>Login</Button>
            </form>
          </div>
        </Modal>

        <Modal open={openSignUp} onClose={() => setOpenSignUp(false)}>
          <div style={modalStyle} className={classes.paper}>
            <form className="app_signin">
              <center>
                <img
                  className="app_headerImage"
                  src="https://www.virtualstacks.com/wp-content/uploads/2019/11/instagram-logo-name.png"
                  alt="Instagram"
                />
              </center>
              <Input placeholder="username" type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
              <Input placeholder="email" type="text" value={email} onChange={(e) => setEmail(e.target.value)} />
              <Input placeholder="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
              <Button type="submit" onClick={signUp}>Sign up</Button>
            </form>
          </div>
        </Modal>

        <div className="app_header">
          <Link to="/">
            <img className="app_headerImage" src="https://raw.githubusercontent.com/loganmarchione/homelab-svg-assets/745e5d9249f2c847d58de5f1fd7ba4de2f63918e/assets/instagram.svg" alt="Instagram" />
          </Link>
          {authToken ? (
            <div>
              <Avatar onClick={handleProfileMenu} src="path_to_profile_picture.jpg" alt="Profile" />
              <Menu
                anchorEl={anchorEl}
                keepMounted
                open={Boolean(anchorEl)}
                onClose={handleCloseMenu}
              >
                <Link to="/profile">
                  <MenuItem onClick={handleCloseMenu}>Profile</MenuItem>
                </Link>
                <MenuItem onClick={signOut}>Logout</MenuItem>
              </Menu>
            </div>
          ) : (
            <div>
              <Button onClick={() => setOpenSignIn(true)}>Login</Button>
              <Button onClick={() => setOpenSignUp(true)}>Signup</Button>
            </div>
          )}
        </div>

        <Routes>
          <Route
            path="/"
            element={<HomePage posts={posts} authToken={authToken} authTokenType={authTokenType} userId={userId} setPosts={setPosts} />}
          />
          <Route
            path="/profile"
            element={<Profile authToken={authToken} authTokenType={authTokenType} userId={userId} />}
          />
          <Route
            path="/profile/:userId"
            element={<Profile authToken={authToken} authTokenType={authTokenType} userId={userId} />}
          />
        </Routes>
      </div>
    </Router>
  );
}

function HomePage({ posts, authToken, authTokenType, userId, setPosts }) {
  return (
    <div className="app_posts">
      {posts.map((post) => (
        <Post key={post.id} post={post} authToken={authToken} authTokenType={authTokenType} setPosts={setPosts} />
      ))}
      {authToken ? (
        <ImageUpload authToken={authToken} authTokenType={authTokenType} userId={userId} setPosts={setPosts} />
      ) : (
        <h3>You need to log in to upload</h3>
      )}
    </div>
  );
}

export default App;