task :default => [:test, :build]

task :test do
  STDERR.puts `python setup.py test`
end

task :build do
  STDERR.puts `python setup.py sdist bdist_egg`
end
