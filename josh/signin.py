from proj import app

# start a sever if the program is being run on its own (not being imported from another module)
# set debug mode to true so that the server reloads itself on code changes
# make the server publicly available to users on the network

if __name__ == '__main__':
  app.debug = True
  app.run(host='localhost', port=4567)