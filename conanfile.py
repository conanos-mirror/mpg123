from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conanos.build import config_scheme
import os,shutil

class Mpg123Conan(ConanFile):
    name = "mpg123"
    version = "1.25.10"
    description = "Fast console MPEG Audio Player and decoder library"
    url = "https://github.com/conanos/mpg123"
    homepage = "https://www.mpg123.de/"
    license = "LGPL-2.1"
    exports = ["COPYING"]
    generators = "visual_studio", "gcc"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { 'shared': True, 'fPIC': True }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def source(self):
        url_ = 'https://nchc.dl.sourceforge.net/project/mpg123/mpg123/{version}/mpg123-{version}.tar.bz2'
        tools.get(url_.format(version=self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        #with tools.chdir(self._source_subfolder):
        #    self.run("autoreconf -f -i")

        #    autotools = AutoToolsBuildEnvironment(self)
        #    _args = ["--prefix=%s/builddir"%(os.getcwd()), "--with-audio=dummy"]
        #    if self.options.shared:
        #        _args.extend(['--enable-shared=yes','--enable-static=no'])
        #    else:
        #        _args.extend(['--enable-shared=no','--enable-static=yes'])
        #    autotools.configure(args=_args)
        #    autotools.make(args=["-j4"])
        #    autotools.install()
        if self.settings.os == 'Windows':
            with tools.chdir(os.path.join(self._source_subfolder,"ports","MSVC++","2015","win32")):
                msbuild = MSBuild(self)
                msbuild.build("mpg123.sln",upgrade_project=True,platforms={'x86': 'Win32', 'x86_64': 'x64'})

    def package(self):
        if self.settings.os == 'Windows':
            platforms={'x86': 'Win32', 'x86_64': 'x64'}
            output_relpath=os.path.join(self._source_subfolder,"ports","MSVC++","2015","win32", platforms.get(str(self.settings.arch)), str(self.settings.build_type))
            self.copy("libmpg123.*", dst=os.path.join(self.package_folder,"lib"), src=os.path.join(self.build_folder,output_relpath ),excludes="libmpg123.dll")
            self.copy("libmpg123.dll", dst=os.path.join(self.package_folder,"bin"), src=os.path.join(self.build_folder, output_relpath))
            self.copy("*", dst=os.path.join(self.package_folder,"bin"), src=os.path.join(self.build_folder, output_relpath ), excludes="libmpg123.*")
            self.copy("mpg123.h",dst=os.path.join(self.package_folder,"include"), src=os.path.join(self.build_folder,self._source_subfolder,"ports","MSVC++"))
            
            tools.mkdir(os.path.join(self.package_folder,"lib","pkgconfig"))
            shutil.copyfile(os.path.join(self.build_folder,self._source_subfolder,"libmpg123.pc.in"),
                            os.path.join(self.package_folder,"lib","pkgconfig", "libmpg123.pc"))
            replacements = {
                "@prefix@"          : self.package_folder,
                "@exec_prefix@"     : "${prefix}/bin",
                "@libdir@"          : "${prefix}/lib",
                "@includedir@"      : "${prefix}/include",
                "@PACKAGE_VERSION@" : self.version,
            }
            for s, r in replacements.items():
                tools.replace_in_file(os.path.join(self.package_folder,"lib","pkgconfig", "libmpg123.pc"),s,r)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

