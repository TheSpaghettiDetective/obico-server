import React, { Component, Fragment } from 'react';
import {
  BrowserRouter as Router,
  Redirect,
  Switch,
  Route,
} from 'react-router-dom'

import Nav from './components/Nav';
import CamMain from './components/cam/CamMain';
import logo from './logo.svg';
import './App.css';

class App extends Component {
  render() {
    return (
        <Router>
            <Fragment>
                <Nav />
                <Switch>
                    <Route path="/cam" exact component={CamMain} />
                </Switch>
            </Fragment>
        </Router>
    )
  }
}

export default App;
