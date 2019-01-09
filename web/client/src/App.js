import React, { Component, Fragment } from 'react';
import {
    BrowserRouter as Router,
    Redirect,
    Switch,
    Route,
} from 'react-router-dom'
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import CssBaseline from "@material-ui/core/CssBaseline";

import Nav from './components/Nav';
import CamMain from './components/cam/CamMain';
import logo from './logo.svg';
import './App.css';

const theme = createMuiTheme();

class App extends Component {
    render() {
        return (
            <MuiThemeProvider theme={theme}>
                <div style={{display: 'flex'}}>
                    <CssBaseline />
                    <Router>
                        <Fragment>
                            <Nav />
                            <div style={{height: '100vh', padding: '24px', overflow: 'auto', flexGrow: '1'}}>
                            <Switch>
                                <Route path="/cam" exact component={CamMain} />
                            </Switch>
                            </div>
                        </Fragment>
                    </Router>
                </div>
            </MuiThemeProvider>
        )
    }
}

export default App;
