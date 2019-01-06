import React, { Component } from 'react';
import { withStyles } from '@material-ui/core/styles';
import _ from 'lodash';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';

const styles = theme => ({
  paper: {
    padding: theme.spacing.unit * 2,
    textAlign: 'center',
    color: theme.palette.text.secondary,
  },
  camImg: {
    width: '100%',
  }
});


class CamComponent extends Component {
  state = {detection: null}

  componentDidMount() {
    this.interval = setInterval(() => {
      fetch('/api/detections')
      .then( resp => resp.json() )
      .then( detection => {
        this.setState({detection})
      })
    }, 5000);
  }

  componentWillUnmount() {
    clearInterval(this.interval);
  }

  render() {
    const { classes } = this.props;

    return (
      <div>
        <Grid container spacing={24} justify='center'>
          <Grid item xs={12} md={6} lg={4}>
            <Paper className={classes.paper}>
              <img src={_.get(this.state, 'detection.input_img_url')} className={classes.camImg} />
            </Paper>
          </Grid>
        </Grid>
      </div>
    );
  }
}

export default withStyles(styles)(CamComponent);
